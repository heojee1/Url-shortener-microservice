from sqlalchemy import create_engine, exc, text
import os, re, random
from hashids import Hashids
from time import time
from dotenv import load_dotenv

load_dotenv()

# Read ENV vars
DB_DB = os.environ.get('POSTGRES_DB')
DB_HOST = os.environ.get('POSTGRES_HOST')
DB_PORT = os.environ.get('POSTGRES_PORT')
DB_USER = os.environ.get('POSTGRES_USER')
DB_PASS = os.environ.get('POSTGRES_PASSWORD')
SALT = os.environ.get('HASH_SALT')

URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASS.strip()}@{DB_HOST}:{DB_PORT}/{DB_DB}'

FAIL = False
SUCCESS = True

hashids = Hashids(min_length=8, salt=SALT)

###
# Public functions
###
def is_valid_url(url):
    regex = re.compile(
        r'^(?:http)s?://'  # scheme
        # domain...
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(regex.match(url))


def generate_short_url():
    number = int(round(time() * 1000)) + random.randint(0, 1e8)
    return hashids.encode(number)

def select_url_by_(**kwargs):
    filter_str = ' AND '.join(f"{k}='{v}'" for k, v in kwargs.items())
    
    QUERY = text(f"""SELECT * FROM urls WHERE {filter_str}""")

    db_connection = None
    engine = None
    try:
        engine = create_engine(URI, echo=True)
        db_connection = engine.connect()
        result = db_connection.execute(QUERY).fetchone()
        db_connection.commit()
        if result:
            return result._asdict(), SUCCESS
        return result, SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}', FAIL
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()


def retrieve_all(user_id):    
    QUERY = text(f"""SELECT * FROM urls WHERE user_id={user_id}""")

    db_connection = None
    engine = None
    try:
        engine = create_engine(URI, echo=True)
        db_connection = engine.connect()
        result = db_connection.execute(QUERY).fetchall()
        db_connection.commit()
        return [row._asdict() for row in result], SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}', FAIL
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()


def create_url(url, user_id):
    '''
        Function used to insert a user into the DB.
        :param username: username
        :param password: password
        :return: error or success strings for inserting into DB.
    '''

    try:
        result, _ = select_url_by_(original=url, user_id=user_id)
        print(result)
        assert not result
    except:
        return result, FAIL

    db_connection = None
    engine = None
    try:
        engine = create_engine(URI, echo=True)
        db_connection = engine.connect()

        short = generate_short_url()
        url_info = db_connection.execute(text(f"""
                INSERT INTO urls (original, short, user_id)
                    VALUES ('{url}', '{short}', '{user_id}')
                RETURNING *
                """)).fetchone()
        db_connection.commit()
        return url_info._asdict(), SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}', FAIL
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()


def update_link(id, new_url, user_id):
    '''
        Function used to update username from the DB.
        :param username: username
        :param old_password: old password
        :param new_password: new password
        :return: error or success strings for updating DB.
    '''

    db_connection = None
    engine = None

    try:
        engine = create_engine(URI, echo=True)
        db_connection = engine.connect()

        url_info = db_connection.execute(text(f'''
            UPDATE
                urls
            SET
                original='{new_url}'
            WHERE
                id={id} AND user_id={user_id}
            RETURNING *
            ''')).fetchone()
        db_connection.commit()
        return url_info._asdict(), SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}', FAIL
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()


def remove_url(id, user_id):
    '''
        Function used to delete a url from the DB.
        :param id: url ID
        :return: error or success strings for updating DB.
    '''

    db_connection = None
    engine = None
    try:
        engine = create_engine(URI, echo=True)
        db_connection = engine.connect()
        url_info = db_connection.execute(text(f'''
            DELETE FROM
                urls
            WHERE
                id={id} AND user_id={user_id}
            RETURNING *''')).fetchone()
        db_connection.commit()
        return url_info._asdict(), SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}'
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()