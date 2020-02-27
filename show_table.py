import os
import psycopg2

import common
import db_config


def main(db: db_config.DBSettings):
    connection = psycopg2.connect(
        user=db.user,
        host=db.host,
        port=db.port,
        password=os.environ.get('POSTGRES_PASSWORD', None),
    )
    connection.autocommit = True
    cursor = connection.cursor()

    print('End state of the table:')
    cursor.execute(f'SELECT * FROM {common.TABLE_NAME}')
    print('id, value')
    for row in cursor:
        print(f'{row[0]}, {row[1]}')


if __name__ == '__main__':
    args = common.arg_parser().parse_args()
    main(db_config.DATABASES[args.db])
