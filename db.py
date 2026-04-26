import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

# Connection pool — reuses connections instead of creating new ones
pool = []
POOL_SIZE = 5

def get_connection():
    if pool:
        return pool.pop()
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('DB_SERVER')};"
        f"DATABASE={os.getenv('DB_NAME')};"
        f"Trusted_Connection=yes;"
        f"timeout=30;"
    )
    return conn

def release_connection(conn):
    if len(pool) < POOL_SIZE:
        pool.append(conn)
    else:
        conn.close()

def query(sql, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows
    finally:
        release_connection(conn)

def execute(sql, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
    finally:
        release_connection(conn)

def call_sp(sp_name, params=()):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        placeholders = ','.join(['?' for _ in params])
        cursor.execute(f"EXEC {sp_name} {placeholders}", params)
        conn.commit()
    finally:
        release_connection(conn)