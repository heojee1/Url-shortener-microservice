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

# Create URI for Postgresql database
URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASS.strip()}@{DB_HOST}:{DB_PORT}/{DB_DB}'

FAIL = False
SUCCESS = True

hashids = Hashids(min_length=8, salt=SALT)

next_id = 0

def generate_short_url():
    global next_id

    number = int(round(time() * 1000)) + random.randint(0, 1e6) + next_id
    next_id += 1

    return hashids.encode(number)


# We got the basic structure of the function and SQL queries from this tutorial online 
# https://www.digitalocean.com/community/tutorials/how-to-use-a-postgresql-database-in-a-flask-application#step-5-adding-new-books

# Select a url by given keyword arguments 
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

# Retrieve all urls under the given username
def retrieve_all(username):    
    QUERY = text(f"""SELECT * FROM urls WHERE username='{username}'""")

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


def create_url(url, username):
    '''
        Function used to insert a user into the DB.
        :param username: username
        :param password: password
        :return: error or success strings for inserting into DB.
    '''

    try:
        result, _ = select_url_by_(original=url, username=username)
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
        db_connection.execute(text(f"""
                INSERT INTO urls (original, short, username)
                    VALUES ('{url}', '{short}', '{username}')
                """))
        db_connection.commit()
        return "Done", SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}', FAIL
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()


# Update the url of the given id under the username
def update_link(id, new_url, username):
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

        counts = db_connection.execute(text(f'''
            UPDATE
                urls
            SET
                original='{new_url}'
            WHERE
                id={id} AND username='{username}'
            '''))
        db_connection.commit()
        return counts.rowcount, SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}', FAIL
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()


# Remoeve the url by id under the given username
def remove_url(id, username):
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
        counts = db_connection.execute(text(f'''
            DELETE FROM
                urls
            WHERE
                id={id} AND username='{username}'
            '''))
        db_connection.commit()
        return counts.rowcount, SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}', FAIL
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()


# Remove all urls under the given username
def remove_all_url(username):
    '''
        Function used to delete all urls of the user from the DB.
        :param username: username
        :return: error or success strings for updating DB.
    '''

    db_connection = None
    engine = None
    try:
        engine = create_engine(URI, echo=True)
        db_connection = engine.connect()
        counts = db_connection.execute(text(f'''
            DELETE FROM
                urls
            WHERE
                username='{username}'
            '''))
        db_connection.commit()
        return counts.rowcount, SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}', FAIL
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()

# Select a user by the given keyword arguments
def select_user_by_(**kwargs):
    filter_str = ' AND '.join(f"{k}='{v}'" for k, v in kwargs.items())
    
    QUERY = text(f"""SELECT * FROM users WHERE {filter_str}""")

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