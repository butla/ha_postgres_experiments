import common
import db_config


def main(db: db_config.DBSettings):
    print('Waiting for the DB...')
    cursor = common.new_cursor(db.host, db.port, db.user)

    print(f'Dropping old {common.TABLE_NAME} table if it exists...')
    cursor.execute(f'DROP TABLE IF EXISTS {common.TABLE_NAME}')
    print(f'Creating {common.TABLE_NAME} table with some rows...')
    cursor.execute(f'CREATE TABLE {common.TABLE_NAME}(id SERIAL primary key, value BIGINT)')
    for _ in range(10):
        cursor.execute(f'INSERT INTO {common.TABLE_NAME}(value) values (0);')
    print('Done.')


if __name__ == '__main__':
    args = common.arg_parser().parse_args()
    main(db_config.DATABASES[args.db])
