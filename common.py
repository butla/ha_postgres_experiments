import argparse
import os

from tenacity import retry, wait_fixed, wait_random
import psycopg2


TABLE_NAME = 'bla'


@retry(
    wait=wait_fixed(1) + wait_random(0, 2),
)
def new_cursor(host: str, port: int, user: str):
    connection = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=os.environ.get('POSTGRES_PASSWORD', None),
    )
    connection.autocommit = True
    return connection.cursor()


def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default=0, type=int,
                        help='DB config to use from db_config.py')
    return parser
