import itertools
import time

import psycopg2

import common
import db_config

# TODO metrics with prometheus?


def main(
        target_db_id: int = 1,
        successful_writes_target: int = 10000,
):
    def cursor_generator():
        # just round robin, disregarding the config
        for db_settings in itertools.cycle(db_config.DATABASES):
            print('switching DB settings to:', db_settings)
            yield common.new_cursor(db_settings.host, db_settings.port, db_settings.user)

    sql = f"""
    UPDATE {common.TABLE_NAME}
    SET value = value + 1
    WHERE ID={target_db_id};
    """
    print('Starting writes...', flush=True)
    cursor_gen = cursor_generator()
    cursor = next(cursor_gen)

    successes = 0
    i = 0
    while successes != successful_writes_target:
        # TODO replace counting with prometheus
        i += 1
        if i % 100 == 0:
            print('Iteration:', i, flush=True)

        try:
            cursor.execute(sql)
            successes += 1
        except psycopg2.Error:
            print('PG Error!', flush=True)
            time.sleep(3)
            cursor = next(cursor_gen)
    print('Done', flush=True)


def _parse_args():
    parser = common.arg_parser()
    parser.add_argument('--target-id', default=1, type=int)
    parser.add_argument('--successful-writes-target', default=10000, type=int,
                        help='only use 1 through 10')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    main(
        target_db_id=args.target_id,
        successful_writes_target=args.successful_writes_target,
    )
