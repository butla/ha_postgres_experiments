#!/bin/bash
# This experiment shows that we're doing an additional write with the current python scripts

if [ ! -v VIRTUAL_ENV ]; then
    echo ERROR! Run this in virtual env!
    exit 1
fi
TARGET_WRITES=3000
export POSTGRES_PASSWORD=KLeUo9LfMvllD_zQLWTDvA

set -e

# this is so that we wait for the DB to get up here
python reset_db.py

read -p "HIT A KEY to start spam"

python hit_db.py --target-id 1 --successful-writes-target $TARGET_WRITES &
python hit_db.py --target-id 2 --successful-writes-target $TARGET_WRITES &
python hit_db.py --target-id 3 --successful-writes-target $TARGET_WRITES &
python hit_db.py --target-id 4 --successful-writes-target $TARGET_WRITES &

sleep 15
echo "--- will kill master node"
ssh root@142.93.131.34 docker kill pg_primary
ssh root@64.227.47.75 "docker exec pg_secondary su postgres -c 'pg_ctl promote'"


echo "--- waiting for DB writers to finish up..."
wait

echo "--- experiment summary, all values should show ${TARGET_WRITES} or 1 more!"
python show_table.py --db 1

# kill_secondary_pg
# docker volume rm $PRIMARY_PG > /dev/null
# docker volume rm $SECONDARY_PG > /dev/null
# docker volume rm $BACKUP_VOLUME > /dev/null
# docker network rm $DOCKER_NETWORK > /dev/null
