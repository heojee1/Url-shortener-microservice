from sqlalchemy import create_engine, exc, text
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv

load_dotenv()

# Read ENV vars
DB_DB = os.environ.get('POSTGRES_DB')
DB_HOST = os.environ.get('POSTGRES_HOST')
DB_PORT = os.environ.get('POSTGRES_PORT')
DB_USER = os.environ.get('POSTGRES_USER')
DB_PASS = os.environ.get('POSTGRES_PASSWORD')

URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASS.strip()}@{DB_HOST}:{DB_PORT}/{DB_DB}'

FAIL = False
SUCCESS = True

###
# Public functions
###
def select_user_by_id(user_id):    
    QUERY = text(f"""SELECT * FROM users WHERE id={user_id}""")

    db_connection = None
    engine = None
    try:
        engine = create_engine(URI, echo=True)
        db_connection = engine.connect()
        user = db_connection.execute(QUERY).fetchone()
        db_connection.commit()
        return user._asdict(), SUCCESS
    except exc.SQLAlchemyError as error:
        return f'Error while executing DB query: {error}', FAIL
    finally:
        if db_connection: db_connection.close()
        if engine: engine.dispose()
