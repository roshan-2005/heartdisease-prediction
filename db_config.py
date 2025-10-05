import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DB_URL = os.getenv("DB_URL")

def get_connection():
    """
    Returns a psycopg2 connection object
    """
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        return None

def test_connection():
    conn = get_connection()
    if conn:
        print("✅ Successfully connected to NeonDB!")
        conn.close()
    else:
        print("⚠️ Connection failed.")

# Test connection
if __name__ == "__main__":
    test_connection()
