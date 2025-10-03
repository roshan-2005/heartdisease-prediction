import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_mysql_connection():
    try:
        # Try both localhost and 127.0.0.1 to avoid pipe errors
        for host in ['127.0.0.1', 'localhost']:
            try:
                conn = mysql.connector.connect(
                    host=host,
                    user=os.getenv('DB_USER', 'root'),  # Default to 'root' if not set
                    password=os.getenv('DB_PASSWORD', 'VcR@2005 '),  # Default empty password
                    database=os.getenv('DB_NAME', 'cardio_ai'),
                    port=int(os.getenv('DB_PORT', 3306)),  # Ensure port is integer
                    connect_timeout=5  # Fail faster if connection isn't working
                )
                print(f"✅ Successfully connected to MySQL at {host}!")
                conn.close()
                return True
            except mysql.connector.Error as err:
                print(f"⚠️ Failed to connect at {host}: {err}")
                continue
        
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if MySQL service is running (services.msc)")
        print("2. Verify your password in .env file matches MySQL")
        print("3. Try 'mysql -u root -p' in Command Prompt to test manually")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

# Run the test
test_mysql_connection()