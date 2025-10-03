import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import streamlit as st
import time

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.database = os.getenv('DB_NAME', 'cardio_ai')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', 'VcR@2005')
        
    def create_connection(self):
        """Create and return a database connection"""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                passwd=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            st.error(f"Error connecting to MySQL: {e}")
            return None
    
    def create_user(self, username, email, password_hash):
        """Create a new user in the database"""
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query, (username, email, password_hash))
                connection.commit()
                return cursor.lastrowid
            except Error as e:
                st.error(f"Error creating user: {e}")
                return None
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
    
    def get_user_by_username(self, username):
        """Retrieve a user by username"""
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = "SELECT * FROM users WHERE username = %s"
                cursor.execute(query, (username,))
                return cursor.fetchone()
            except Error as e:
                st.error(f"Error fetching user: {e}")
                return None
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def get_user_by_id(self, user_id):
        """Retrieve a user by user ID"""
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = "SELECT * FROM users WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                return cursor.fetchone()
            except Error as e:
                st.error(f"Error fetching user: {e}")
                return None
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
    
    def create_patient(self, user_id, full_name, date_of_birth, gender, contact_number):
        """Create a new patient profile"""
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                # Generate unique ID
                unique_id = f"PAT-{user_id}-{int(time.time())}"
                
                query = """
                INSERT INTO patients (user_id, unique_id, full_name, date_of_birth, gender, contact_number)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (user_id, unique_id, full_name, date_of_birth, gender, contact_number))
                connection.commit()
                return unique_id
            except Error as e:
                st.error(f"Error creating patient: {e}")
                return None
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
    
    def get_patient_by_user(self, user_id):
        """Get patient profile by user ID"""
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = "SELECT * FROM patients WHERE user_id = %s"
                cursor.execute(query, (user_id,))
                return cursor.fetchone()
            except Error as e:
                st.error(f"Error fetching patient: {e}")
                return None
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
    
    def update_patient(self, patient_id, full_name, date_of_birth, gender, contact_number):
        """Update patient profile information in the database"""
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                UPDATE patients 
                SET full_name = %s, 
                    date_of_birth = %s, 
                    gender = %s, 
                    contact_number = %s
                WHERE patient_id = %s
                """
                cursor.execute(query, (
                    full_name,
                    date_of_birth,
                    gender,
                    contact_number,
                    patient_id
                ))
                connection.commit()
                return True
            except Error as e:
                st.error(f"Error updating patient: {e}")
                return False
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
    
    def save_health_record(self, patient_id, input_data, risk_score, risk_category, notes=None):
        """Save a health record to the database"""
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                query = """
                INSERT INTO health_records 
                (patient_id, age, gender, bmi, chol, tg, hdl, ldl, risk_score, risk_category, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                # Convert all numerical values to native Python float
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
                connection.commit()
                return cursor.lastrowid
            except Error as e:
                st.error(f"Error saving health record: {e}")
                return None
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
    
    def get_patient_records(self, patient_id):
        """Get all health records for a patient"""
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                query = """
                SELECT * FROM health_records 
                WHERE patient_id = %s
                ORDER BY created_at DESC
                """
                cursor.execute(query, (patient_id,))
                return cursor.fetchall()
            except Error as e:
                st.error(f"Error fetching records: {e}")
                return None
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def delete_user(self, user_id):
        """Delete a user and all associated data from the database"""
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                
                # First get patient_id if exists
                cursor.execute(
                    "SELECT patient_id FROM patients WHERE user_id = %s", 
                    (user_id,)
                )
                patient_id = cursor.fetchone()
                
                if patient_id:
                    patient_id = patient_id[0]
                    # Delete health records
                    cursor.execute(
                        "DELETE FROM health_records WHERE patient_id = %s",
                        (patient_id,)
                    )
                    
                    # Delete patient
                    cursor.execute(
                        "DELETE FROM patients WHERE user_id = %s",
                        (user_id,)
                    )
                
                # Finally delete the user
                cursor.execute(
                    "DELETE FROM users WHERE user_id = %s",
                    (user_id,)
                )
                
                connection.commit()
                return True
            except Error as e:
                st.error(f"Error deleting user: {e}")
                connection.rollback()
                return False
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()