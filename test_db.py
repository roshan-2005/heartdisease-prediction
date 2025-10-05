import os
from dotenv import load_dotenv
import psycopg2

# Explicitly load the .env from the current folder
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

DB_URL = os.getenv("DB_URL")
print("DB_URL =", DB_URL)  # Should print your full Neon URL

if not DB_URL:
    print("ERROR: DB_URL not found. Check your .env file.")
else:
    try:
        conn = psycopg2.connect(DB_URL)
        print("✅ Connected to NeonDB!")
        conn.close()
    except Exception as e:
        print("Connection failed:", e)
