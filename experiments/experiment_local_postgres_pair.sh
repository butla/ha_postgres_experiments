#!/bin/bash
# This experiment shows that we're doing an additional write with the current python scripts

if [ ! -v VIRTUAL_ENV ]; then
    echo ERROR! Run this in virtual env!
    exit 1
fi
TARGET_WRITES=6000

set -e

DOCKER_NETWORK=pg
PRIMARY_PG=pg_primary
SECONDARY_PG=pg_secondary
BACKUP_VOLUME=pg_backup
SECONDARY_PORT=5433
export POSTGRES_PASSWORD=KLeUo9LfMvllD_zQLWTDvA


function run_primary_pg() {
    echo "--- Starting primary postgres..."
    docker run --rm -d \
        --name $PRIMARY_PG \
        --net $DOCKER_NETWORK \
        -p 5432:5432 \
        -v ${PRIMARY_PG}:/var/lib/postgresql/data \
        -v ${BACKUP_VOLUME}:/backup \
        -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
        $PRIMARY_PG:latest > /dev/null
}

function run_secondary_pg() {
    echo "--- Starting secondary postgres..."
    docker run --rm -d \
        --name $SECONDARY_PG \
        --net $DOCKER_NETWORK \
        -p ${SECONDARY_PORT}:5432 \
        -v ${BACKUP_VOLUME}:/var/lib/postgresql/data \
        -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
        postgres:12.2 \
        postgres \
        -c "primary_conninfo=postgresql://postgres:${POSTGRES_PASSWORD}@${PRIMARY_PG}" > /dev/null
}

function kill_primary_pg() {
    echo "--- Killing primary postgres!"
    docker kill $PRIMARY_PG > /dev/null
}

function kill_secondary_pg() {
    echo "--- Killing secondary postgres!"
    docker kill $SECONDARY_PG > /dev/null
}

docker build -t $PRIMARY_PG -f dockerfiles/primary.Dockerfile dockerfiles

docker network create $DOCKER_NETWORK > /dev/null
docker volume create $PRIMARY_PG > /dev/null
docker volume create $SECONDARY_PG > /dev/null
docker volume create $BACKUP_VOLUME > /dev/null

echo "--- running containers"

run_primary_pg
# this is so that we wait for the DB to get up here
python reset_db.py

echo "--- backing up primary's data to serve as the secondary's data files"
docker exec $PRIMARY_PG pg_basebackup -D /backup/ -U postgres

echo "--- making sure seconday will start as a standby"
docker exec $PRIMARY_PG touch /backup/standby.signal

run_secondary_pg

# if we did that without the secondary on-line, the db wouldn't accept connections
echo "--- enabling synchronous standby in the primary"
docker exec $PRIMARY_PG bash -c "echo \"synchronous_standby_names = '*'\" >> /var/lib/postgresql/data/postgresql.conf"
docker exec $PRIMARY_PG su postgres -c 'pg_ctl reload'

python hit_db.py --target-id 1 --successful-writes-target $TARGET_WRITES &
python hit_db.py --target-id 2 --successful-writes-target $TARGET_WRITES &
python hit_db.py --target-id 3 --successful-writes-target $TARGET_WRITES &
python hit_db.py --target-id 4 --successful-writes-target $TARGET_WRITES &

sleep 5

kill_primary_pg
docker exec $SECONDARY_PG su postgres -c 'pg_ctl promote'

echo "--- waiting for DB writers to finish up..."
wait

echo "--- experiment summary, all values should show ${TARGET_WRITES} or 1 more!"
python show_table.py --db 1

kill_secondary_pg
docker volume rm $PRIMARY_PG > /dev/null
docker volume rm $SECONDARY_PG > /dev/null
docker volume rm $BACKUP_VOLUME > /dev/null
docker network rm $DOCKER_NETWORK > /dev/null
