import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import streamlit as st
import time

# ------------------- Load .env -------------------
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    st.error("ERROR: DB_URL not found in .env. Make sure your .env file exists and is correct.")
else:
    print("Using DB_URL:", DB_URL)  # Debug: confirm Neon URL

# ------------------- Database Manager -------------------
class DatabaseManager:
    
    # ------------------- User Methods -------------------
    def create_user(self, username, email, password_hash):
        if self.get_user_by_username(username) or self.get_user_by_email(email):
            st.error("Username or email already exists")
            return None

        conn = None
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO users (username, email, password_hash)
                    VALUES (%s, %s, %s)
                    RETURNING user_id
                """
                cursor.execute(query, (username, email, password_hash))
                user_id = cursor.fetchone()[0]
                conn.commit()
                return user_id
        except Exception as e:
            st.error(f"Error creating user: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_user_by_username(self, username):
        conn = None
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                return cursor.fetchone()
        except Exception as e:
            st.error(f"Error fetching user: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_user_by_email(self, email):
        conn = None
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                return cursor.fetchone()
        except Exception as e:
            st.error(f"Error fetching user by email: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_user_by_id(self, user_id):
        conn = None
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                return cursor.fetchone()
        except Exception as e:
            st.error(f"Error fetching user: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def delete_user(self, user_id):
        conn = None
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor() as cursor:
                cursor.execute("SELECT patient_id FROM patients WHERE user_id = %s", (user_id,))
                result = cursor.fetchone()
                if result:
                    patient_id = result[0]
                    cursor.execute("DELETE FROM health_records WHERE patient_id = %s", (patient_id,))
                    cursor.execute("DELETE FROM patients WHERE user_id = %s", (user_id,))
                cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                conn.commit()
                return True
        except Exception as e:
            st.error(f"Error deleting user: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    # ------------------- Patient Methods -------------------
    def create_patient(self, user_id, full_name, date_of_birth, gender, contact_number):
        conn = None
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor() as cursor:
                unique_id = f"PAT-{user_id}-{int(time.time())}"
                query = """
                    INSERT INTO patients (user_id, unique_id, full_name, date_of_birth, gender, contact_number)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING patient_id
                """
                cursor.execute(query, (user_id, unique_id, full_name, date_of_birth, gender, contact_number))
                patient_id = cursor.fetchone()[0]
                conn.commit()
                return unique_id
        except Exception as e:
            st.error(f"Error creating patient: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_patient_by_user(self, user_id):
        conn = None
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM patients WHERE user_id = %s", (user_id,))
                return cursor.fetchone()
        except Exception as e:
            st.error(f"Error fetching patient: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def update_patient(self, patient_id, full_name, date_of_birth, gender, contact_number):
        conn = None
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor() as cursor:
                query = """
                    UPDATE patients
                    SET full_name = %s,
                        date_of_birth = %s,
                        gender = %s,
                        contact_number = %s
                    WHERE patient_id = %s
                """
                cursor.execute(query, (full_name, date_of_birth, gender, contact_number, patient_id))
                conn.commit()
                return True
        except Exception as e:
            st.error(f"Error updating patient: {e}")
            return False
        finally:
            if conn:
                conn.close()

    # ------------------- Health Records -------------------
    def save_health_record(self, patient_id, input_data, risk_score, risk_category, notes=None):
        conn = None
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor() as cursor:
                query = """
                    INSERT INTO health_records
                    (patient_id, age, gender, bmi, chol, tg, hdl, ldl, risk_score, risk_category, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING record_id
                """
                cursor.execute(query, (
                    patient_id,
                    float(input_data['age']),
                    input_data['gender'],
                    float(input_data['bmi']),
                    float(input_data['chol']),
                    float(input_data['tg']),
                    float(input_data['hdl']),
                    float(input_data['ldl']),
                    float(risk_score),
                    risk_category,
                    notes
                ))
                record_id = cursor.fetchone()[0]
                conn.commit()
                return record_id
        except Exception as e:
            st.error(f"Error saving health record: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def get_patient_records(self, patient_id):
        conn = None
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT * FROM health_records
                    WHERE patient_id = %s
                    ORDER BY created_at DESC
                """
                cursor.execute(query, (patient_id,))
                return cursor.fetchall()
        except Exception as e:
            st.error(f"Error fetching records: {e}")
            return None
        finally:
            if conn:
                conn.close()
