import psycopg2
import os
from dotenv import load_dotenv

load_dotenv() 

def get_db_connection():
    """Establish and return a new database connection."""
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        print("Database Connection successful!")  # Success message
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

# def list_tables():
#     """List all tables in the database."""
#     conn = get_db_connection()
#     if conn:
#         try:
#             with conn.cursor() as cursor:
#                 cursor.execute("""
#                     SELECT table_name 
#                     FROM information_schema.tables
#                     WHERE table_schema = 'public'
#                     AND table_type = 'BASE TABLE';
#                 """)
#                 tables = cursor.fetchall()
#                 for table in tables:
#                     print(table[0])
#         finally:
#             conn.close()

# list_tables()