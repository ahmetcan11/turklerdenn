from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
import os, sys
from dotenv import load_dotenv
from core.config import settings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
sys.path.append(BASE_DIR)
db_host = os.environ.get('DB_HOST', 'localhost')  # Replace 'localhost' with your default host
db_port = os.environ.get('DB_PORT', '5432')  # Replace '5432' with your default port
db_user = os.environ.get('DB_USER', 'your_username')  # Replace 'your_username' with your default username
db_pass = os.environ.get('DB_PASS', 'your_password')  # Replace 'your_password' with your default password
db_name = os.environ.get('DB_NAME', 'your_database')  # Replace 'your_database' with your default database name
cloud_sql_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME', 'cloud')
query = {"unix_sock" : "/cloudsql/{}/.s.PGSQL.5432".format(
    os.environ.get("CLOUD_SQL_CONNECTION_NAME"),
    )
}

# db_url = URL(
#     drivername="postgresql+psycopg2",
#     username=db_user,
#     password=db_pass,
#     database=db_name,
#     query=query
# )
db_url = os.environ.get('DB_URL_LOCAL', 'DB_URL')

engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
