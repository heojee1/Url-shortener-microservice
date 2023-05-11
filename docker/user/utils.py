import os

from sqlalchemy import create_engine, exc, text
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

# Read ENV vars
DB_DB = os.environ.get('POSTGRES_DB')
DB_HOST = os.environ.get('POSTGRES_HOST')
DB_PORT = os.environ.get('POSTGRES_PORT')
DB_USER = os.environ.get('POSTGRES_USER')
DB_PASS = os.environ.get('POSTGRES_PASSWORD')
SECRET = os.environ.get('SECRET')

URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASS.strip()}@{DB_HOST}:{DB_PORT}/{DB_DB}'

FAIL = False
SUCCESS = True

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
        
# Create a user with given username and password
def create_user(username, password):
    '''
        Function used to insert a user into the DB.
        :param username: username
        :param password: password
        :return: error or success strings for inserting into DB.
    '''

    try:
        result, _ = select_user_by_(username=username)
        assert not result
    except:
        return result, FAIL

    db_connection = None
    engine = None
    try:
        engine = create_engine(URI, echo=True)
        db_connection = engine.connect()
        db_connection.execute(text(f"""
                INSERT INTO users (username, password)
                    VALUES ('{username}', '{generate_password_hash(password)}')
                """))
        db_connection.commit()
        return "Insert successful", SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}', FAIL
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()

# Update user's password with new password
def update_password(username, old_password, new_password):
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
        user, _ = select_user_by_(username=username)
        assert check_password_hash(user['password'], old_password)
    except:
        return None, FAIL

    try:
        engine = create_engine(URI, echo=True)
        db_connection = engine.connect()

        db_connection.execute(text(f'''
            UPDATE
                users
            SET
                password='{generate_password_hash(new_password)}'
            WHERE
                username='{username}'
            '''))
        db_connection.commit()
        return user, SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}', FAIL
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()