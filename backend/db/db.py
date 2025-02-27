import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import psycopg2
from alembic import command
from alembic.config import Config
from subprocess import run
from db.models import Base
from sqlalchemy.exc import ProgrammingError

### To run table updates do these:
# alembic revision --autogenerate
# alembic upgrade head

# Load environment variables from .env file
load_dotenv()

# Get the DATABASE_URL from the .env file
DATABASE_URL = os.getenv("DATABASE_URL")

def create_db():
    # Extract the database name from the DATABASE_URL
    db_name = DATABASE_URL.split('/')[-1]

    # Create a connection to the PostgreSQL server (without specifying a database)
    server_engine = create_engine(DATABASE_URL.rsplit('/', 1)[0])

    # Connect to the server to check if the database exists
    with server_engine.connect() as conn:
        query = text("SELECT 1 FROM pg_database WHERE datname = :db_name")
        result = conn.execute(query, {'db_name': db_name})  # Use dictionary for parameterized query
        if result.fetchone():
            print(f"Database '{db_name}' already exists.")
        else:
            # Create the database using psycopg2, bypassing the transaction block
            print(f"Creating database '{db_name}'...")
            conn.close()  # Close the SQLAlchemy connection first
            conn_psycopg2 = psycopg2.connect(
                host="localhost", user="postgres", password="password"  # Replace with your credentials
            )
            conn_psycopg2.autocommit = True  # Disable transactions for this connection
            cursor = conn_psycopg2.cursor()
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully.")
            cursor.close()
            conn_psycopg2.close()

    # Now that the database exists, we can connect to it
    engine = create_engine(DATABASE_URL)

    # Checking if tables exist or if they need to be created
    print("Checking if tables need to be created or updated...")
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        print("Tables created/updated successfully.")
    except Exception as e:
        print(f"Error creating/updating tables: {e}")

    # Check if the tables already exist to avoid duplicate table errors
    with engine.connect() as connection:
        try:
            result = connection.execute(text("SELECT to_regclass('public.admin');"))
            if result.fetchone()[0]:
                print("The 'admin' table already exists, skipping creation.")
            else:
                print("The 'admin' table does not exist, creating it.")
        except ProgrammingError as e:
            print("Error checking table existence:", e)

    # Run `stamp` to mark Alembic's version table as up-to-date
    print("Stamping the database to mark it as up-to-date.")
    try:
        run(["alembic", "stamp", "head"])  # Use Alembic's stamp command to mark as up-to-date
        print("Database schema is up-to-date.")
    except Exception as e:
        print(f"Error stamping the database: {e}")

    # Check for migrations and apply any if there are changes in models
    alembic_config = Config("alembic.ini")  # Path to your alembic.ini file

    print("Running migrations (if any changes are detected)...")
    try:
        command.upgrade(alembic_config, "head")  # Apply any migrations to get to the latest state
        print("Migrations applied successfully.")
    except Exception as e:
        print(f"Error applying migrations: {e}")

    # If everything is up-to-date
    print("Database is up-to-date!")

if __name__ == "__main__":
    create_db()
