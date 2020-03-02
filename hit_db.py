import itertools
import time
from time import perf_counter

import prometheus_client
import psycopg2

import common
import db_config


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
    success_metric = prometheus_client.Counter('successful_writes', 'How many passed DB writes.')
    write_times = prometheus_client.Summary('write_times', 'How long successful writes took.')

    while successes != successful_writes_target:
        try:
            query_start = perf_counter()

            cursor.execute(sql)

            successes += 1
            success_metric.inc()
            write_times.observe(perf_counter() - query_start)
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
    parser.add_argument('--prometheus-port', default=8000, type=int,
                        help='needs to be different for every instance')
    return parser.parse_args()


if __name__ == '__main__':
    args = _parse_args()
    prometheus_client.start_http_server(args.prometheus_port)
    main(
        target_db_id=args.target_id,
        successful_writes_target=args.successful_writes_target,
    )
