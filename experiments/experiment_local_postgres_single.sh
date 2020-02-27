#!/bin/bash
# This experiment shows that we're doing an additional write with the current python scripts

if [ ! -v VIRTUAL_ENV ]; then
    echo ERROR! Run this in virtual env!
    exit 1
fi
TARGET_WRITES=6000

set -e

PG_CONTAINER_ID=''

function run_pg() {
    echo "--- Starting postgres..."
    PG_CONTAINER_ID=$(docker run --rm -d \
        -p 5432:5432 \
        -v pgdata:/var/lib/postgresql/data \
        -e POSTGRES_HOST_AUTH_METHOD=trust \
        postgres:12.2)
}

function kill_pg() {
    echo "--- Killing postgres!"
    docker kill $PG_CONTAINER_ID > /dev/null
}

docker volume create pgdata
run_pg

python reset_db.py
python hit_db.py --target-id 1 --successful-writes-target $TARGET_WRITES &
python hit_db.py --target-id 2 --successful-writes-target $TARGET_WRITES &

sleep 5
kill_pg
run_pg

echo "--- waiting for DB writers to finish up..."
wait

echo "--- experiment summary, all values should show ${TARGET_WRITES}!"
python show_table.py

kill_pg
docker volume rm pgdata
