import logging
import sqlalchemy


def create_engine(user, password, database, host='127.0.0.1', port=5432):
    """
    Creates database engine

    :param user: database user
    :param password: database password
    :param database: database name
    :param host: database host (default 127.0.0.1)
    :param port: database port (default 5432)
    :return: database engine created by sqlalchemy
    """
    db_url = ['postgresql', '://', user, ':', password, '@', host, ':', str(port), '/',
              database]
    logging.debug('PgSQL database url:' + ''.join(db_url))
    return sqlalchemy.create_engine(''.join(db_url))


def create_tables(engine):
    """
    Creates iBis database structure (empty tables).

    :rtype : boolean
    :param engine: sqlalchemy engine for databse to create table in
    :return: True on success, False on failure
    """
    # TODO
    return True
