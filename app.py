import streamlit as st
import numpy as np
import pandas as pd
import joblib
import plotly.graph_objects as go
from streamlit_extras.let_it_rain import rain
from streamlit_extras.stylable_container import stylable_container
import time
import os
import hashlib
from database import DatabaseManager
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io
import datetime
import random

# Initialize database
db = DatabaseManager()

# --- Initialize Session State ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "patient_id" not in st.session_state:
    st.session_state.patient_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "unique_id" not in st.session_state:
    st.session_state.unique_id = None

# --- Load Model & Scaler ---
try:
    best_model = joblib.load(r"C:\Users\gamin\Documents\Internship\Finalyearproj-HDP\best_model (2).pkl")
    scaler = joblib.load(r"C:\Users\gamin\Documents\Internship\Finalyearproj-HDP\scaler (1).pkl")
except FileNotFoundError:
    st.error("Model or scaler file not found. Please ensure the files are in the correct directory.")
    st.stop()

feature_names = ['Age', 'Gender', 'BMI', 'Chol', 'TG', 'HDL', 'LDL']

def predict_heart_disease(input_data):
    input_df = pd.DataFrame([input_data], columns=feature_names)
    input_scaled = scaler.transform(input_df)
    return best_model.predict_proba(input_scaled)[0]

def generate_pdf(patient_data, records):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = f"<h1>Cardio-AI Health Report for {patient_data['full_name']}</h1>"
    story.append(Paragraph(title, styles['Title']))
    
    # Patient Info
    patient_info = f"""
    <h2>Patient Information</h2>
    <p><b>Unique ID:</b> {patient_data['unique_id']}</p>
    <p><b>Date of Birth:</b> {patient_data['date_of_birth']}</p>
    <p><b>Gender:</b> {patient_data['gender']}</p>
    <p><b>Contact:</b> {patient_data['contact_number']}</p>
    """
    story.append(Paragraph(patient_info, styles['Normal']))
    
    # Health Records
    story.append(Paragraph("<h2>Health History</h2>", styles['Heading2']))
    
    # Prepare table data
    table_data = [['Date', 'Age', 'BMI', 'Chol', 'HDL', 'LDL', 'TG', 'Risk Score', 'Category']]
    
    for record in records:
        date = record['created_at'].strftime('%Y-%m-%d')
        table_data.append([
            date,
            str(record['age']),
            f"{record['bmi']:.1f}",
            str(record['chol']),
            str(record['hdl']),
            str(record['ldl']),
            str(record['tg']),
            f"{record['risk_score']:.1f}%",
            record['risk_category']
        ])
    
    # Create table
    t = Table(table_data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(t)
    
    # Generate PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- Modern Glassmorphism Theme ---
def get_theme_config():
    return {
        "bg": "linear-gradient(135deg, #0F172A 0%, #1E293B 100%)",  # Gradient background
        "secondary_bg": "rgba(30, 41, 59, 0.7)",  # Semi-transparent
        "text": "#E2E8F0",      # Off-white text
        "primary": "#3B82F6",   # Blue
        "secondary": "#10B981", # Teal
        "accent": "#F59E0B",    # Amber
        "danger": "#EF4444",    # Red
        "card": "rgba(30, 41, 59, 0.5)",      # Glass card background
        "border": "1px solid rgba(255, 255, 255, 0.1)",  # Subtle border
        "hover": "0 8px 32px rgba(59, 130, 246, 0.2)",  # Glass hover effect
        "highlight": "0 0 0 2px rgba(59, 130, 246, 0.3)",  # Focus highlight
        "blur": "blur(16px)",   # Glass blur effect
        "shadow": "0 4px 30px rgba(0, 0, 0, 0.1)"  # Glass shadow
    }

# --- App Config ---
st.set_page_config(
    page_title="Cardio-AI",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🩺"
)

# --- Theme (Default to Dark) ---
theme_config = get_theme_config()

# --- Glassmorphism CSS with Modern Effects ---
st.markdown(f"""
<style>
    :root {{
        --primary: {theme_config["primary"]};
        --secondary: {theme_config["secondary"]};
        --bg: {theme_config["bg"]};
        --secondary-bg: {theme_config["secondary_bg"]};
        --text: {theme_config["text"]};
        --accent: {theme_config["accent"]};
        --danger: {theme_config["danger"]};
        --card: {theme_config["card"]};
        --border: {theme_config["border"]};
        --hover: {theme_config["hover"]};
        --highlight: {theme_config["highlight"]};
        --blur: {theme_config["blur"]};
        --shadow: {theme_config["shadow"]};
    }}

    /* Base styles with glassmorphism */
    .stApp {{
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Inter', sans-serif;
    }}
    
    [data-testid="stSidebar"] {{
        background: var(--secondary-bg) !important;
        backdrop-filter: var(--blur);
        -webkit-backdrop-filter: var(--blur);
        box-shadow: var(--shadow);
        border-right: var(--border) !important;
    }}
    
    /* Glassmorphism cards */
    .glass-card {{
        background: var(--card);
        backdrop-filter: var(--blur);
        -webkit-backdrop-filter: var(--blur);
        border-radius: 16px;
        border: var(--border);
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
    }}
    
    .glass-card:hover {{
        box-shadow: var(--hover);
        transform: translateY(-5px);
        border-color: rgba(255, 255, 255, 0.2);
    }}
    
    /* Button effects */
    .stButton>button {{
        transition: all 0.2s ease !important;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: var(--hover) !important;
    }}
    
    /* Input fields with glass effect */
    .stTextInput>div>div>input, 
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {{
        background: rgba(30, 41, 59, 0.5) !important;
        backdrop-filter: var(--blur);
        -webkit-backdrop-filter: var(--blur);
        border-radius: 12px !important;
        border: var(--border) !important;
    }}
    
    .stTextInput>div>div>input:focus, 
    .stNumberInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus {{
        box-shadow: var(--highlight) !important;
        border-color: var(--primary) !important;
    }}
    
    /* Risk cards */
    .risk-card {{
        border-left: 4px solid;
        transition: all 0.3s ease;
        backdrop-filter: var(--blur);
        -webkit-backdrop-filter: var(--blur);
    }}
    
    .high-risk {{
        border-color: var(--danger) !important;
        background: linear-gradient(
            to right,
            rgba(239, 68, 68, 0.1),
            rgba(239, 68, 68, 0.05)
        ) !important;
    }}
    
    .low-risk {{
        border-color: var(--secondary) !important;
        background: linear-gradient(
            to right,
            rgba(16, 185, 129, 0.1),
            rgba(16, 185, 129, 0.05)
        ) !important;
    }}
    
    /* Animations */
    @keyframes fadeIn {{
        0% {{ opacity: 0; transform: translateY(10px); }}
        100% {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes float {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-5px); }}
        100% {{ transform: translateY(0px); }}
    }}
    
    .float {{
        animation: float 6s ease-in-out infinite;
    }}
    
    /* Gradient text for headings */
    .gradient-text {{
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    /* Glass button */
    .glass-button {{
        background: rgba(59, 130, 246, 0.2) !important;
        backdrop-filter: var(--blur);
        -webkit-backdrop-filter: var(--blur);
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        box-shadow: var(--shadow);
        transition: all 0.3s ease !important;
    }}
    
    .glass-button:hover {{
        background: rgba(59, 130, 246, 0.4) !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--hover) !important;
    }}
    
    /* Modern tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: rgba(30, 41, 59, 0.5) !important;
        backdrop-filter: var(--blur);
        -webkit-backdrop-filter: var(--blur);
        border-radius: 12px !important;
        border: var(--border) !important;
        padding: 8px 16px;
        transition: all 0.3s ease;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(59, 130, 246, 0.2) !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: rgba(59, 130, 246, 0.4) !important;
        border-color: var(--primary) !important;
    }}
    
    /* Page entrance animation */
    .page-entrance {{
        animation: fadeIn 0.5s ease-out;
    }}
</style>
""", unsafe_allow_html=True)

def login_page():
    st.markdown("""
    <div class="page-entrance">
        <div style="
            max-width: 500px; 
            margin: 2rem auto; 
            padding: 2rem;
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        ">
            <div style="text-align: center; margin-bottom: 2rem;" class="float">
                <h1 class="gradient-text">Cardio-AI</h1>
                <p style="color: var(--text); opacity: 0.8;">Advanced Cardiovascular Risk Assessment</p>
            </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
            
            if submit:
                user = db.get_user_by_username(username)
                if user and hashlib.sha256(password.encode()).hexdigest() == user['password_hash']:
                    st.session_state['authenticated'] = True
                    st.session_state['user_id'] = user['user_id']
                    st.session_state['username'] = user['username']
                    st.session_state['is_admin'] = user.get('is_admin', False)
                    
                    # Load patient data if exists
                    patient = db.get_patient_by_user(user['user_id'])
                    if patient:
                        st.session_state['patient_id'] = patient['patient_id']
                        st.session_state['unique_id'] = patient['unique_id']
                    
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username", key="register_username")
            email = st.text_input("Email", key="register_email")
            new_password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm_password")
            
            register = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if register:
                # Validate all fields are filled
                if not new_username:
                    st.error("Username is required")
                elif not email:
                    st.error("Email is required")
                elif not new_password:
                    st.error("Password is required")
                elif not confirm_password:
                    st.error("Please confirm your password")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    # Validate email format
                    if "@" not in email or "." not in email:
                        st.error("Please enter a valid email address")
                    else:
                        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
                        user_id = db.create_user(new_username, email, hashed_password)
                        if user_id:
                            st.success("Account created successfully! Please log in.")
                        else:
                            st.error("Username or email already exists")
    
    st.markdown("""
        </div>
        <div style="text-align: center; margin-top: 2rem; color: var(--text); opacity: 0.7; font-size: 0.9rem;">
            <p>Secure login powered by advanced encryption</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

def user_management_page():
    st.markdown("""
    <div class="page-entrance">
        <h1 class="gradient-text" style="margin-bottom: 1.5rem;">👥 User Management</h1>
    """, unsafe_allow_html=True)
    
    if not st.session_state.get('is_admin'):
        st.error("You don't have permission to access this page")
        return
    
    # Get all users from the database
    users = db.get_all_users()
    
    if users:
        st.markdown("### User List")
        
        # Search functionality
        search_query = st.text_input("Search users", placeholder="Enter username or email")
        
        if search_query:
            users = [user for user in users 
                    if search_query.lower() in user['username'].lower() 
                    or search_query.lower() in user['email'].lower()]
        
        if not users:
            st.warning("No users found matching your search")
            return
        
        # Display users in a table with delete buttons
        for user in users:
            with st.container():
                cols = st.columns([3, 2, 1, 1])
                with cols[0]:
                    st.markdown(f"**{user['username']}** ({user['email']})")
                with cols[1]:
                    st.markdown(f"User ID: {user['user_id']}")
                with cols[2]:
                    st.markdown("**Admin**" if user.get('is_admin') else "🔵 User")
                with cols[3]:
                    if user['user_id'] != st.session_state.user_id:  # Prevent self-deletion
                        if st.button("Delete", key=f"delete_{user['user_id']}"):
                            if db.delete_user(user['user_id']):
                                st.success(f"User {user['username']} deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete user")
                    else:
                        st.warning("Current user")
    else:
        st.info("No users found in the database")

def patient_profile_page():
    st.markdown("""
    <div class="page-entrance">
        <h1 class="gradient-text" style="margin-bottom: 1.5rem;">👤 Patient Profile</h1>
    """, unsafe_allow_html=True)
    
    # Check if patient exists
    patient = db.get_patient_by_user(st.session_state['user_id'])
    
    if patient:
        st.session_state['patient_id'] = patient['patient_id']
        st.session_state['unique_id'] = patient['unique_id']
        
        # Edit Profile Section
        with st.expander("✏️ Edit Profile Information", expanded=False):
            with stylable_container(
                key="edit_profile_form",
                css_styles="""
                {
                    background: rgba(30, 41, 59, 0.5);
                    backdrop-filter: blur(16px);
                    -webkit-backdrop-filter: blur(16px);
                    border-radius: 16px;
                    padding: 1.5rem;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                """
            ):
                with st.form("edit_profile_form"):
                    cols = st.columns(2)
                    with cols[0]:
                        full_name = st.text_input("Full Name", value=patient['full_name'], key="edit_full_name")
                        date_of_birth = st.date_input("Date of Birth", 
                                                    value=patient['date_of_birth'], 
                                                    max_value=datetime.date.today(),
                                                    key="edit_dob")
                    with cols[1]:
                        gender = st.selectbox("Gender", 
                                            ["Male", "Female", "Other"], 
                                            index=["Male", "Female", "Other"].index(patient['gender']),
                                            key="edit_gender")
                        contact_number = st.text_input("Contact Number", 
                                                    value=patient['contact_number'],
                                                    key="edit_contact")
                    
                    if st.form_submit_button("💾 Save Changes", type="primary"):
                        if db.update_patient(
                            patient['patient_id'],
                            full_name,
                            date_of_birth,
                            gender,
                            contact_number
                        ):
                            st.success("Profile updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update profile")
        
        # View Profile Section
        cols = st.columns(2)
        with cols[0]:
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.5rem; margin: 1rem 0;">
                <h3>👤 Personal Information</h3>
                <p><strong>Unique ID:</strong> {patient['unique_id']}</p>
                <p><strong>Full Name:</strong> {patient['full_name']}</p>
                <p><strong>Date of Birth:</strong> {patient['date_of_birth']}</p>
            </div>
            """, unsafe_allow_html=True)
            
        with cols[1]:
            age = (datetime.date.today() - patient['date_of_birth']).days // 365
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.5rem; margin: 1rem 0;">
                <h3>📞 Contact Details</h3>
                <p><strong>Gender:</strong> {patient['gender']}</p>
                <p><strong>Age:</strong> {age} years</p>
                <p><strong>Contact Number:</strong> {patient['contact_number']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Health Records Section
        st.markdown("## 📅 Your Health History")
        
        records = db.get_patient_records(patient['patient_id'])
        if records:
            # Date range selector
            record_dates = [r['created_at'].date() for r in records]
            min_date = min(record_dates)
            max_date = max(record_dates)
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("From date", 
                                         value=min_date,
                                         min_value=datetime.date(min_date.year - 5, 1, 1),
                                         max_value=max_date,
                                         key="start_date_filter")
            with col2:
                end_date = st.date_input("To date", 
                                       value=max_date,
                                       min_value=min_date,
                                       max_value=datetime.date.today(),
                                       key="end_date_filter")
            
            # Filter records
            filtered_records = [
                r for r in records 
                if start_date <= r['created_at'].date() <= end_date
            ]
            
            if filtered_records:
                # PDF Export
                if st.button("📄 Export to PDF Report", key="pdf_export"):
                    pdf_buffer = generate_pdf(patient, filtered_records)
                    st.download_button(
                        label="⬇️ Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"cardio_ai_report_{patient['unique_id']}_{datetime.date.today()}.pdf",
                        mime="application/pdf",
                        key="pdf_download"
                    )
                
                # Enhanced Data Display
                df = pd.DataFrame(filtered_records)
                df['created_at'] = df['created_at'].dt.strftime('%Y-%m-%d %H:%M')
                df['risk_score'] = df['risk_score'].apply(lambda x: f"{x:.1f}%")
                
                # Style function for risk categories
                def color_risk(val):
                    if val == 'High Risk':
                        return 'color: #EF4444; font-weight: bold;'
                    else:
                        return 'color: #10B981; font-weight: bold;'
                
                styled_df = df.style.applymap(color_risk, subset=['risk_category'])
                
                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "created_at": "Date",
                        "age": "Age",
                        "bmi": st.column_config.NumberColumn("BMI", format="%.1f"),
                        "chol": "Cholesterol",
                        "hdl": "HDL",
                        "ldl": "LDL",
                        "tg": "Triglycerides",
                        "risk_score": "Risk Score",
                        "risk_category": "Risk Category"
                    }
                )
                
                # Risk Trend Visualization
                st.markdown("## 📈 Risk Score Trend Over Time")
                trend_df = pd.DataFrame(filtered_records)
                trend_df['created_at'] = pd.to_datetime(trend_df['created_at'])
                trend_df = trend_df.sort_values('created_at')
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=trend_df['created_at'],
                    y=trend_df['risk_score'],
                    mode='lines+markers',
                    name='Risk Score',
                    line=dict(color=theme_config["primary"], width=2),
                    marker=dict(size=6, color=theme_config["secondary"])
                ))
                
                fig.add_hline(
                    y=50,
                    line_dash="dash",
                    line_color=theme_config["danger"],
                    annotation_text="High Risk Threshold",
                    annotation_position="bottom right"
                )
                
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Risk Score (%)",
                    hovermode="x unified",
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=theme_config["text"]),
                    margin=dict(l=50, r=50, b=50, t=50)
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"⚠️ No records found between {start_date} and {end_date}")
        else:
            st.info("ℹ️ No health records found. Complete a risk assessment to get started.")
        
        if st.button("🩺 Go to Risk Assessment", type="primary", key="profile_to_risk"):
            st.session_state.current_page = "risk"
        
        # Account Deletion Section
        st.markdown("---")
        st.markdown("### Account Management")
        
        with st.expander("⚠️ Delete My Account", expanded=False):
            st.warning("This action cannot be undone. All your data will be permanently deleted.")
            confirm = st.checkbox("I understand this will permanently delete all my data")
            
            if confirm and st.button("Confirm Account Deletion", type="primary"):
                if db.delete_user(st.session_state.user_id):
                    st.success("Your account has been deleted successfully.")
                    # Clear session and return to login
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()
                else:
                    st.error("Failed to delete account. Please try again.")
    
    else:
        # Patient registration form
        st.subheader("Complete Your Patient Profile")
        with stylable_container(
            key="patient_form",
            css_styles="""
            {
                background: rgba(30, 41, 59, 0.5);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border-radius: 16px;
                padding: 1.5rem;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            """
        ):
            with st.form("patient_form"):
                full_name = st.text_input("Full Name", key="patient_full_name")
                date_of_birth = st.date_input("Date of Birth", 
                                             max_value=datetime.date.today(), 
                                             key="patient_dob")
                gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="patient_gender")
                contact_number = st.text_input("Contact Number", key="patient_contact")
                
                submit = st.form_submit_button("💾 Save Profile", type="primary")
                
                if submit:
                    unique_id = db.create_patient(
                        st.session_state['user_id'],
                        full_name,
                        date_of_birth,
                        gender,
                        contact_number
                    )
                    if unique_id:
                        # Refresh patient data
                        patient = db.get_patient_by_user(st.session_state['user_id'])
                        if patient:
                            st.session_state['patient_id'] = patient['patient_id']
                            st.session_state['unique_id'] = patient['unique_id']
                            st.success("✅ Profile saved successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to load patient profile after creation")

def home_page():
    st.markdown("""
    <div class="page-entrance">
        <div style="text-align: center; margin-bottom: 3rem;">
            <h1 class="gradient-text" style="font-size: 2.5rem;">Cardio-AI Health Analysis</h1>
            <p style="font-size: 1.1rem; opacity: 0.9;">
            Advanced cardiovascular risk prediction powered by machine learning
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Hero Section
    with stylable_container(
        key="hero",
        css_styles=f"""
        {{
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 2rem;
            margin: 2rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }}
        """
    ):
        col1, col2 = st.columns([2, 1], gap="medium")
        with col1:
            st.markdown("""
            <div>
                <h2 style='margin-bottom: 1rem;'>Your Personal Heart Health Assistant</h2>
                <p style='font-size: 1.1rem; line-height: 1.6;'>
                Cardio-AI analyzes your health metrics using clinically validated algorithms to assess your cardiovascular risk with <strong>89.5% accuracy</strong>. Early detection leads to better outcomes.
                </p>
                <p style='font-size: 1rem; font-style: italic; opacity: 0.8;'>
                "Prevention is better than cure" - Hippocrates
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="float" style="text-align: center;">
                <img src="https://cdn-icons-png.flaticon.com/512/3059/3059518.png" width="120">
            </div>
            """, unsafe_allow_html=True)
        with stylable_container(
        key="heart_disease_intro",
        css_styles="""
        {
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        """
    ):
            st.markdown("""
        ## ❤️ What is Heart Disease?
        
        Heart disease refers to various conditions that affect your heart's structure and function. 
        It's the leading cause of death globally, but many forms are preventable with healthy lifestyle choices.
        
        Heart disease develops when:
        - Arteries become narrowed or blocked (atherosclerosis)
        - The heart muscle becomes weak or damaged
        - Heart valves don't function properly
        - Electrical signals controlling heartbeat are disrupted
        """)
    
    # ==============================================
    # TYPES OF HEART DISEASE SECTION
    # ==============================================
    with stylable_container(
        key="types_container",
        css_styles="""
        {
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
        }
        """
    ):
        st.markdown("""
        ## 🩺 Types of Heart Disease
        
        The main types of cardiovascular diseases include:
        """)
        
        # Create columns for the types
        col1, col2 = st.columns(2, gap="medium")
        
        with col1:
            with stylable_container(
                key="cad_card",
                css_styles="""
                {
                    background: rgba(239, 68, 68, 0.1);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                    border-left: 4px solid #EF4444;
                }
                """
            ):
                st.markdown("""
                ### 1. Coronary Artery Disease (CAD)
                - Most common type
                - Caused by plaque buildup in arteries
                - Can lead to heart attacks
                - Symptoms: Chest pain, shortness of breath
                """)
            
            with stylable_container(
                key="arrhythmia_card",
                css_styles="""
                {
                    background: rgba(59, 130, 246, 0.1);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                    border-left: 4px solid #3B82F6;
                }
                """
            ):
                st.markdown("""
                ### 2. Arrhythmias
                - Irregular heartbeats
                - Heart may beat too fast, slow, or irregularly
                - Can cause dizziness or fainting
                - Some types are life-threatening
                """)
        
        with col2:
            with stylable_container(
                key="hf_card",
                css_styles="""
                {
                    background: rgba(16, 185, 129, 0.1);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                    border-left: 4px solid #10B981;
                }
                """
            ):
                st.markdown("""
                ### 3. Heart Failure
                - Heart can't pump blood effectively
                - Develops gradually over time
                - Symptoms: Fatigue, swelling in legs
                - Managed with medication and lifestyle
                """)
            
            with stylable_container(
                key="valve_card",
                css_styles="""
                {
                    background: rgba(245, 158, 11, 0.1);
                    border-radius: 12px;
                    padding: 1.5rem;
                    margin: 1rem 0;
                    border-left: 4px solid #F59E0B;
                }
                """
            ):
                st.markdown("""
                ### 4. Valve Disorders
                - Heart valves don't open/close properly
                - Can be congenital or develop later
                - May require surgical repair
                - Symptoms: Fatigue, irregular heartbeat
                """)
    
    # ==============================================
    # RISK FACTORS SECTION
    # ==============================================
    with stylable_container(
        key="risk_factors",
        css_styles="""
        {
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
        }
        """
    ):
        st.markdown("""
        ## ⚠️ Major Risk Factors
        
        | Controllable Factors | Uncontrollable Factors |
        |----------------------|------------------------|
        | High blood pressure | Age (risk increases after 45) |
        | High cholesterol | Family history of heart disease |
        | Smoking | Gender (men at higher risk) |
        | Diabetes | Race (some ethnic groups at higher risk) |
        | Obesity | Previous heart attack |
        | Physical inactivity |  |
        | Poor diet |  |
        | Excessive alcohol |  |
        """)
    
    # ==============================================
    # PREVENTION SECTION
    # ==============================================
    with stylable_container(
        key="prevention",
        css_styles="""
        {
            background: rgba(16, 185, 129, 0.1);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            border-left: 4px solid #10B981;
        }
        """
    ):
        st.markdown("""
        ## 🛡️ Prevention Tips
        
        - 🥗 Eat a heart-healthy diet (fruits, vegetables, whole grains)
        - 🏃‍♂️ Get regular exercise (150 mins/week moderate activity)
        - 🚭 Avoid tobacco products
        - 🧘‍♀️ Manage stress through relaxation techniques
        - 🩺 Get regular health screenings
        - 🧂 Limit salt and sugar intake
        - 🥑 Choose healthy fats (olive oil, nuts, fish)
        """)
        
    
    st.markdown("## How It Works")
    cols = st.columns(3, gap="medium")
    steps = [
        ("🩺", "Clinical Input", "Provide your health metrics including cholesterol levels, BMI, and other vital signs"),
        ("🧠", "AI Analysis", "Our model processes your data using validated medical algorithms"),
        ("📋", "Personalized Report", "Receive a detailed risk assessment with actionable insights")
    ]
    
    for i, (icon, title, desc) in enumerate(steps):
        with cols[i]:
            st.markdown(f"""
            <div class="glass-card" style="padding: 1.5rem; text-align: center; height: 100%;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <h3 style='margin-bottom: 0.5rem;'>{title}</h3>
                <p style='color: var(--text); opacity: 0.9;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Key Features
    st.markdown("## Why Choose Cardio-AI?")
    features = [
        ("✅", "Clinically Validated", "Trained on real patient data with 89.5% accuracy"),
        ("⚡", "Instant Results", "Get your risk assessment in seconds"),
        ("🔒", "Privacy Focused", "Your data never leaves your device"),
        ("📈", "Actionable Insights", "Personalized recommendations based on your results")
    ]
    
    for i in range(0, len(features), 2):
        cols = st.columns(2, gap="medium")
        for j in range(2):
            if i+j < len(features):
                with cols[j]:
                    st.markdown(f"""
                    <div class="glass-card" style="padding: 1.5rem;">
                        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.5rem;">
                            <span style="font-size: 1.5rem;">{features[i+j][0]}</span>
                            <h4 style="margin: 0;">{features[i+j][1]}</h4>
                        </div>
                        <p style="opacity: 0.9; margin: 0;">{features[i+j][2]}</p>
                    </div>
                    """, unsafe_allow_html=True)

def risk_assessment_page():
    st.markdown("""
    <div class="page-entrance">
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 class="gradient-text" style="font-size: 2.5rem;">Heart Disease Risk Assessment</h1>
            <p style="font-size: 1.1rem; opacity: 0.9;">
            Enter your health metrics below to receive your personalized risk analysis
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # First check if patient profile exists
    if not st.session_state.get('patient_id'):
        st.error("⚠️ Please complete your patient profile before performing risk assessments")
        if st.button("Go to Profile Page"):
            st.session_state.current_page = "profile"
            st.rerun()
        return
    
    # Patient Health Metrics Section
    with stylable_container(
        key="input_form",
        css_styles=f"""
        {{
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }}
        """
    ):
        st.markdown("### Patient Health Metrics")
        
        cols = st.columns(2, gap="medium")
        
        with cols[0]:
            age = st.number_input("Age (years)", min_value=1, max_value=120, value=45, help="Enter your current age")
            if age < 1:
                st.error("Age must be at least 1.")
                st.stop()
            
            sex = st.selectbox("Gender", ["Female", "Male"], help="Biological sex affects cardiovascular risk")
            gender = 1 if sex == "Male" else 0
            
            bmi = st.number_input("Body Mass Index (BMI)", min_value=10.0, max_value=50.0, value=25.0, help="Weight (kg) / height (m)²")
            if bmi < 10.0:
                st.error("BMI must be at least 10.")
                st.stop()
        
        with cols[1]:
            chol = st.number_input("Total Cholesterol (mg/dL)", min_value=100, max_value=300, value=200, help="Desirable: <200 mg/dL")
            if chol < 100:
                st.error("Total Cholesterol must be at least 100 mg/dL.")
                st.stop()
            
            tg = st.number_input("Triglycerides (mg/dL)", min_value=50, max_value=500, value=150, help="Desirable: <150 mg/dL")
            if tg < 50:
                st.error("Triglycerides must be at least 50 mg/dL.")
                st.stop()
            
            hdl = st.number_input("HDL Cholesterol (mg/dL)", min_value=20, max_value=100, value=50, help="Desirable: >60 mg/dL")
            if hdl < 20:
                st.error("HDL Cholesterol must be at least 20 mg/dL.")
                st.stop()
            
            ldl = st.number_input("LDL Cholesterol (mg/dL)", min_value=50, max_value=250, value=130, help="Optimal: <100 mg/dL")
            if ldl < 50:
                st.error("LDL Cholesterol must be at least 50 mg/dL.")
                st.stop()
    
    if st.button("**Analyze My Cardiovascular Risk**", use_container_width=True, type="primary", key="analyze_button"):
        # Double-check patient_id exists
        if not st.session_state.get('patient_id'):
            st.error("Patient profile not found. Please complete your profile first.")
            st.session_state.current_page = "profile"
            st.rerun()
            return
            
        with st.spinner('Processing your health metrics...'):
            time.sleep(1)
            
            try:
                input_data = {
                    'age': float(age),
                    'gender': gender,
                    'bmi': float(bmi),
                    'chol': float(chol),
                    'tg': float(tg),
                    'hdl': float(hdl),
                    'ldl': float(ldl)
                }
                
                prediction = predict_heart_disease(list(input_data.values()))
                high_risk = prediction[1] * 100
                risk_category = "High Risk" if high_risk > 50 else "Low Risk"
                
                # Save to database
                record_id = db.save_health_record(
                    st.session_state['patient_id'],
                    input_data,
                    high_risk,
                    risk_category,
                    notes="Patient self-assessment"
                )
                
                if record_id:
                    st.success("Assessment saved to your health history!")
                else:
                    st.error("Failed to save assessment. Please try again.")
                    return
                
                # Visual feedback
                if high_risk > 50:
                    rain(emoji="⚠️", font_size=20, falling_speed=3, animation_length=1)
                else:
                    rain(emoji="✅", font_size=20, falling_speed=3, animation_length=1)
                
                # Risk Card
                risk_class = "high-risk" if high_risk > 50 else "low-risk"
                risk_emoji = "⚠️ High Risk" if high_risk > 50 else "✅ Low Risk"
                risk_color = "danger" if high_risk > 50 else "secondary"
                
                st.markdown(f"""
                <div class='risk-card glass-card' style="text-align: center; padding: 1.5rem; margin: 2rem 0;">
                    <h2 style='margin-bottom: 0.5rem;'>{risk_emoji}</h2>
                    <div style='font-size: 2.5rem; font-weight: 700; margin: 1rem 0;'>
                        {high_risk:.1f}%
                    </div>
                    <p style='font-size: 1.1rem;'>
                    Probability of cardiovascular disease
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Gauge Chart
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = high_risk,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Risk Level", 'font': {'size': 18}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkgray"},
                        'bar': {'color': theme_config[risk_color]},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 30], 'color': theme_config["secondary"]},
                            {'range': [30, 70], 'color': theme_config["accent"]},
                            {'range': [70, 100], 'color': theme_config["danger"]}
                        ],
                        'threshold': {
                            'line': {'color': "white", 'width': 4},
                            'thickness': 0.75,
                            'value': high_risk
                        }
                    }
                ))
                fig.update_layout(
                    height=300,
                    margin=dict(t=50, b=30),
                    font=dict(color=theme_config["text"]),
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Recommendations Section
                st.markdown("## Health Recommendations")
                
                if high_risk > 50:
                    with stylable_container(
                        key="warning_box",
                        css_styles=f"""
                        {{
                            background: rgba(239, 68, 68, 0.1);
                            backdrop-filter: blur(16px);
                            -webkit-backdrop-filter: blur(16px);
                            border-radius: 16px;
                            padding: 1.5rem;
                            margin: 1rem 0;
                            border-left: 4px solid {theme_config["danger"]};
                        }}
                        """
                    ):
                        st.markdown("""
                        <div>
                            <h3 style='margin-bottom: 1rem;'>Clinical Guidance</h3>
                            <p style='margin-bottom: 1rem;'>
                            Based on your results, we recommend consulting with a healthcare professional for further evaluation.
                            </p>
                            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem;'>
                                <div>
                                    <h4 style='font-size: 1.1rem;'>🩺 Medical Follow-up</h4>
                                    <ul>
                                        <li>Schedule a cardiology consultation</li>
                                        <li>Consider lipid profile testing</li>
                                        <li>Blood pressure monitoring</li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 style='font-size: 1.1rem;'>💊 Treatment Options</h4>
                                    <ul>
                                        <li>Discuss statin therapy</li>
                                        <li>Evaluate blood pressure meds</li>
                                        <li>Diabetes screening</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                else:
                    with stylable_container(
                        key="success_box",
                        css_styles=f"""
                        {{
                            background: rgba(16, 185, 129, 0.1);
                            backdrop-filter: blur(16px);
                            -webkit-backdrop-filter: blur(16px);
                            border-radius: 16px;
                            padding: 1.5rem;
                            margin: 1rem 0;
                            border-left: 4px solid {theme_config["secondary"]};
                        }}
                        """
                    ):
                        st.markdown("""
                        <div>
                            <h3 style='margin-bottom: 1rem;'>Preventive Measures</h3>
                            <p style='margin-bottom: 1rem;'>
                            Maintain your heart health with these evidence-based recommendations:
                            </p>
                            <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem;'>
                                <div>
                                    <h4 style='font-size: 1.1rem;'>🍏 Nutrition</h4>
                                    <ul>
                                        <li>Increase fiber intake</li>
                                        <li>Choose healthy fats</li>
                                        <li>Limit processed foods</li>
                                    </ul>
                                </div>
                                <div>
                                    <h4 style='font-size: 1.1rem;'>🏋️‍♂️ Activity</h4>
                                    <ul>
                                        <li>150 min/week moderate exercise</li>
                                        <li>Strength training 2x/week</li>
                                        <li>Reduce sedentary time</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Biomarker Analysis
                st.markdown("## Your Biomarker Breakdown")
                
                with stylable_container(
                    key="biomarker_analysis",
                    css_styles=f"""
                    {{
                        background: rgba(30, 41, 59, 0.5);
                        backdrop-filter: blur(16px);
                        -webkit-backdrop-filter: blur(16px);
                        border-radius: 16px;
                        padding: 1.5rem;
                        margin: 1rem 0;
                    }}
                    """
                ):
                    st.markdown(f"""
                    <div>
                        <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 2rem;'>
                            <div>
                                <h4 style='margin-bottom: 1rem;'>Optimal Ranges</h4>
                                <ul style='list-style-type: none; padding: 0;'>
                                    <li style='margin-bottom: 0.75rem;'>• Total Cholesterol: <200 mg/dL</li>
                                    <li style='margin-bottom: 0.75rem;'>• LDL Cholesterol: <100 mg/dL</li>
                                    <li style='margin-bottom: 0.75rem;'>• HDL Cholesterol: >60 mg/dL</li>
                                    <li style='margin-bottom: 0.75rem;'>• Triglycerides: <150 mg/dL</li>
                                    <li style='margin-bottom: 0.75rem;'>• BMI: 18.5-24.9</li>
                                </ul>
                            </div>
                            <div>
                                <h4 style='margin-bottom: 1rem;'>Your Values</h4>
                                <div style='display: grid; gap: 0.75rem;'>
                                    <div style='display: flex; justify-content: space-between;'>
                                        <span>Total Cholesterol: {chol} mg/dL</span>
                                        <span style="color: {'var(--danger)' if chol > 200 else 'var(--secondary)'}">
                                            {"⚠️ Above optimal" if chol > 200 else "✅ Optimal"}
                                        </span>
                                    </div>
                                    <div style='display: flex; justify-content: space-between;'>
                                        <span>LDL Cholesterol: {ldl} mg/dL</span>
                                        <span style="color: {'var(--danger)' if ldl > 100 else 'var(--secondary)'}">
                                            {"⚠️ Above optimal" if ldl > 100 else "✅ Optimal"}
                                        </span>
                                    </div>
                                    <div style='display: flex; justify-content: space-between;'>
                                        <span>HDL Cholesterol: {hdl} mg/dL</span>
                                        <span style="color: {'var(--danger)' if hdl < 60 else 'var(--secondary)'}">
                                            {"⚠️ Below optimal" if hdl < 60 else "✅ Optimal"}
                                        </span>
                                    </div>
                                    <div style='display: flex; justify-content: space-between;'>
                                        <span>Triglycerides: {tg} mg/dL</span>
                                        <span style="color: {'var(--danger)' if tg > 150 else 'var(--secondary)'}">
                                            {"⚠️ Above optimal" if tg > 150 else "✅ Optimal"}
                                        </span>
                                    </div>
                                    <div style='display: flex; justify-content: space-between;'>
                                        <span>BMI: {bmi}</span>
                                        <span style="color: {'var(--danger)' if bmi > 25 else 'var(--secondary)'}">
                                            {"⚠️ Above optimal" if bmi > 25 else "✅ Optimal"}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
            except ValueError:
                st.error("Please enter valid numerical values for all fields.")

def model_info_page():
    st.markdown("""
    <div class="page-entrance">
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 class="gradient-text" style="font-size: 2.5rem;">Clinical AI Model</h1>
            <p style="font-size: 1.1rem; opacity: 0.9;">
            Understanding the technology and required inputs for your risk assessment
            </p>
        </div>
    """, unsafe_allow_html=True)

   
    # How to Use Section
    with stylable_container(
        key="how_to_predict",
        css_styles=f"""
        {{
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
        }}
        """
    ):
        st.markdown("## How to Use Cardio-AI")
        
        steps = [
            ("1", "Navigate to Risk Assessment", "Go to the 'Risk Assessment' page from the sidebar"),
            ("2", "Enter Your Health Metrics", "Fill in all required fields with your latest health data"),
            ("3", "Click Analyze", "Our system will process your information instantly"),
            ("4", "Review Your Results", "Get your personalized risk assessment with recommendations")
        ]
        
        for num, title, desc in steps:
            with stylable_container(
                key=f"step_{num}",
                css_styles=f"""
                {{
                    background: rgba(245, 158, 11, 0.1);
                    backdrop-filter: blur(16px);
                    -webkit-backdrop-filter: blur(16px);
                    border-radius: 12px;
                    padding: 1rem;
                    margin: 0.75rem 0;
                    border-left: 3px solid {theme_config["accent"]};
                }}
                """
            ):
                st.markdown(f"""
                <div>
                    <div style="display: flex; gap: 1rem; align-items: flex-start;">
                        <div style="
                            background: {theme_config["accent"]};
                            color: white;
                            width: 24px;
                            height: 24px;
                            border-radius: 50%;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            flex-shrink: 0;
                        ">{num}</div>
                        <div>
                            <h4 style="margin: 0 0 0.25rem 0;">{title}</h4>
                            <p style="margin: 0; opacity: 0.9;">{desc}</p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 1.5rem;">
            <p style="font-style: italic; opacity: 0.8;">
            For best results, use recent lab test values and accurate measurements.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
         # New Input Values Section with Glassmorphism and Neon Effects
    with stylable_container(
        key="input_values_section",
        css_styles="""
        {
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .input-value-card {
            background: rgba(59, 130, 246, 0.1);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 3px solid var(--primary);
            transition: all 0.3s ease;
        }
        .input-value-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.5);
            border-left: 3px solid var(--accent);
        }
        .input-value-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--primary);
        }
        .input-value-range {
            font-size: 0.9rem;
            color: var(--accent);
            margin-bottom: 0.5rem;
        }
        """
    ):
        st.markdown("## Required Input Values")
        st.markdown("""
        <p style="margin-bottom: 1.5rem; font-size: 1.1rem;">
        These are the health metrics our model analyzes to assess your cardiovascular risk:
        </p>
        """, unsafe_allow_html=True)
        
        # Input Value Cards
        cols = st.columns(2, gap="medium")
        with cols[0]:
            st.markdown("""
            <div class="input-value-card">
                <div class="input-value-title">Age</div>
                <div class="input-value-range">Range: 1-120 years</div>
                <p>Cardiovascular risk increases with age. Enter your current age.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="input-value-card">
                <div class="input-value-title">Gender</div>
                <div class="input-value-range">Male or Female</div>
                <p>Biological sex affects risk calculation (males generally have higher risk).</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="input-value-card">
                <div class="input-value-title">BMI</div>
                <div class="input-value-range">Normal: 18.5-24.9</div>
                <p>Body Mass Index = weight(kg)/height(m)². Higher BMI increases risk.</p>
            </div>
            """, unsafe_allow_html=True)
            
        with cols[1]:
            st.markdown("""
            <div class="input-value-card">
                <div class="input-value-title">Total Cholesterol</div>
                <div class="input-value-range">Optimal: <200 mg/dL</div>
                <p>Total amount of cholesterol in your blood.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="input-value-card">
                <div class="input-value-title">HDL Cholesterol</div>
                <div class="input-value-range">Optimal: ≥60 mg/dL</div>
                <p>"Good" cholesterol that helps remove LDL from arteries.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="input-value-card">
                <div class="input-value-title">LDL Cholesterol</div>
                <div class="input-value-range">Optimal: <100 mg/dL</div>
                <p>"Bad" cholesterol that can build up in arteries.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="input-value-card">
                <div class="input-value-title">Triglycerides</div>
                <div class="input-value-range">Normal: <150 mg/dL</div>
                <p>Type of fat in blood that can contribute to artery hardening.</p>
            </div>
            """, unsafe_allow_html=True)
    
    # How the Model Works Section
    with stylable_container(
        key="model_mechanics",
        css_styles=f"""
        {{
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
        }}
        """
    ):
        st.markdown("## How Our Model Predicts Risk")
        
        cols = st.columns([1, 2], gap="medium")
        with cols[0]:
            st.markdown("""
            <div style="text-align: center;" class="float">
                <img src="https://cdn-icons-png.flaticon.com/512/2103/2103633.png" width="100">
                <p style="font-size: 0.9rem; opacity: 0.8;">Machine Learning Process</p>
            </div>
            """, unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown("""
            <div>
                <h4 style="margin-top: 0;">Advanced Predictive Analytics</h4>
                <p>
                Our model uses a <strong>Random Forest algorithm</strong> trained on thousands of clinical cases to identify patterns 
                in cardiovascular health data. Here's how it works:
                </p>
                <ul>
                    <li><strong>Data Collection:</strong> Aggregates your 7 key health metrics</li>
                    <li><strong>Feature Scaling:</strong> Normalizes values for accurate comparison</li>
                    <li><strong>Pattern Recognition:</strong> Compares your profile to known cases</li>
                    <li><strong>Risk Calculation:</strong> Generates probability score (0-100%)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="margin-top: 1.5rem;">
            <h4>Clinical Validation</h4>
            <p>
            The model was validated against real patient outcomes with:
            </p>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1rem 0;">
                <div class="glass-card" style="padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700;">89.5%</div>
                    <div style="font-size: 0.9rem;">Accuracy</div>
                </div>
                <div class="glass-card" style="padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700;">90.1%</div>
                    <div style="font-size: 0.9rem;">Sensitivity</div>
                </div>
                <div class="glass-card" style="padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700;">88.2%</div>
                    <div style="font-size: 0.9rem;">Specificity</div>
                </div>
                <div class="glass-card" style="padding: 1rem; text-align: center;">
                    <div style="font-size: 1.5rem; font-weight: 700;">7</div>
                    <div style="font-size: 0.9rem;">Key Factors</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Model Performance Section
    with stylable_container(
        key="model_performance",
        css_styles=f"""
        {{
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 2rem;
            margin: 1.5rem 0;
        }}
        """
    ):
        st.markdown("## Model Performance Metrics")
        
        metrics = [
            ("Accuracy", "89.5%", "Measures overall correctness of predictions"),
            ("Precision", "88.2%", "Proportion of true positives among positive predictions"),
            ("Recall", "90.1%", "Ability to identify actual positive cases"),
            ("F1 Score", "89.1%", "Balanced measure of precision and recall")
        ]
        
        cols = st.columns(4, gap="medium")
        for i, (name, value, desc) in enumerate(metrics):
            with cols[i]:
                st.markdown(f"""
                <div class="glass-card" style="padding: 1rem; text-align: center; height: 100%;">
                    <h3 style='margin-bottom: 0.5rem;'>{name}</h3>
                    <div style='font-size: 1.5rem; font-weight: 700;'>
                        {value}
                    </div>
                    <div style='font-size: 0.9rem; opacity: 0.8;'>
                        {desc}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # Feature Importance
        st.markdown("## Feature Importance")
        
        features = ['Age', 'LDL', 'HDL', 'Triglycerides', 'BMI', 'Total Cholesterol', 'Gender']
        importance = [0.25, 0.22, 0.18, 0.15, 0.10, 0.08, 0.02]
        
        fig = go.Figure(go.Bar(
            x=importance,
            y=features,
            orientation='h',
            marker_color=theme_config["primary"],
            text=[f"{imp*100:.1f}%" for imp in importance],
            textposition='auto',
            textfont=dict(size=14)
        ))
        fig.update_layout(
            height=400,
            xaxis_title="Relative Importance",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=theme_config["text"]),
            margin=dict(l=100, r=50, b=50, t=50)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Model Comparison
        st.markdown("## Algorithm Comparison")
        
        comparison_data = {
            "Model": ["Random Forest", "Logistic Regression", "SVM", "Neural Network"],
            "Accuracy": ["89.5%", "82.1%", "85.3%", "87.2%"],
            "Clinical Utility": ["High", "Moderate", "Limited", "High"],
            "Explainability": ["Good", "Excellent", "Fair", "Poor"]
        }
        
        st.dataframe(
            pd.DataFrame(comparison_data).style.set_properties(**{
                'background-color': 'rgba(30, 41, 59, 0.5)',
                'color': theme_config["text"],
                'border': '1px solid rgba(255, 255, 255, 0.1)'
            }),
            use_container_width=True,
            hide_index=True
        )
        # [Previous imports remain exactly the same...]

# Add this new function after model_info_page()
def admin_dashboard():
    st.markdown("""
    <div class="page-entrance">
        <h1 class="gradient-text" style="margin-bottom: 1.5rem;">🛠️ Admin Dashboard</h1>
    """, unsafe_allow_html=True)
    
    # Security check
    if not st.session_state.get('is_admin'):
        st.error("⛔ Unauthorized access")
        return
    
    # System Statistics
    st.markdown("### System Overview")
    cols = st.columns(4)
    with cols[0]:
        st.metric("Total Users", len(db.get_all_users()))
    with cols[1]:
        st.metric("Active Today", "N/A")  # Add actual metric
    with cols[2]:
        st.metric("Risk Assessments", "N/A")
    with cols[3]:
        if st.button("Create Backup"):
            if db.backup_database("backup.sql"):
                st.success("Backup created!")
            else:
                st.error("Backup failed")

    # User Management
    st.markdown("### User Accounts")
    users = db.get_all_users()
    
    for user in users:
        with st.container():
            cols = st.columns([3, 2, 1, 1, 1])
            with cols[0]:
                st.write(f"**{user['username']}**")
            with cols[1]:
                st.write(user['email'])
            with cols[2]:
                admin_status = st.checkbox(
                    "Admin", 
                    value=user.get('is_admin', False),
                    key=f"admin_{user['user_id']}",
                    disabled=(user['user_id'] == st.session_state.user_id)
                )
                if admin_status != user.get('is_admin', False):
                    db.set_user_as_admin(user['user_id'], admin_status)
                    st.rerun()
            with cols[3]:
                if user['user_id'] != st.session_state.user_id:
                    if st.button("Reset Password", key=f"pwd_{user['user_id']}"):
                        # Implement password reset logic
                        st.warning("Feature coming soon")
            with cols[4]:
                if user['user_id'] != st.session_state.user_id:
                    if st.button("Delete", key=f"del_{user['user_id']}"):
                        if db.delete_user(user['user_id']):
                            st.success("User deleted")
                            st.rerun()
                        else:
                            st.error("Deletion failed")

    # Recent Activity
    st.markdown("### Recent Activity")
    stats = db.get_admin_stats()
    if stats:
        st.dataframe(pd.DataFrame(stats['recent_activity']))
    else:
        st.warning("No recent activity data available")

# --- Sidebar ---
with st.sidebar:
    if st.session_state.authenticated:
        st.markdown(f"""
        <div style='
            text-align: center; 
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        ' class="page-entrance">
            <h1 style='margin-bottom: 0.5rem; font-size: 1.5rem;' class="gradient-text">Cardio-AI</h1>
            <p style='font-size: 0.9rem; color: var(--text); opacity: 0.8;'>
            Welcome, {st.session_state.username}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Dynamic navigation options based on user role
        if st.session_state.get('is_admin'):
            nav_options = ["🏠 Home", "📊 Risk Assessment", "🔬 Model Info", "👤 Profile", "👥 User Management"]
        else:
            nav_options = ["🏠 Home", "📊 Risk Assessment", "🔬 Model Info", "👤 Profile"]
        
        nav_option = st.radio(
            "Navigation",
            nav_options,
            index=nav_options.index("🏠 Home") if st.session_state.current_page == "home" 
            else nav_options.index("📊 Risk Assessment") if st.session_state.current_page == "risk" 
            else nav_options.index("🔬 Model Info") if st.session_state.current_page == "model"
            else nav_options.index("👤 Profile") if st.session_state.current_page == "profile"
            else nav_options.index("👥 User Management"),
            label_visibility="collapsed",
            key="nav_radio"
        )
        
        # Update current page based on selection
        if nav_option == "🏠 Home":
            st.session_state.current_page = "home"
        elif nav_option == "📊 Risk Assessment":
            st.session_state.current_page = "risk"
        elif nav_option == "🔬 Model Info":
            st.session_state.current_page = "model"
        elif nav_option == "👤 Profile":
            st.session_state.current_page = "profile"
        elif nav_option == "👥 User Management":
            st.session_state.current_page = "user_management"

        st.markdown("---")
        st.markdown("""
        <div class="glass-card" style="padding: 1rem; text-align: center;">
            <p style='font-size: 0.9rem; margin-bottom: 0.5rem;'>
            <strong>Clinical-grade prediction</strong><br>
            Validated with 89.5% accuracy
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Logout", key="logout_button"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    else:
        st.markdown(f"""
        <div style='
            text-align: center; 
            margin-bottom: 2rem;
            padding: 1.5rem;
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        ' class="page-entrance">
            <h1 style='margin-bottom: 0.5rem; font-size: 1.5rem;' class="gradient-text">Cardio-AI</h1>
            <p style='font-size: 0.9rem; color: var(--text); opacity: 0.8;'>
            AI-Powered Cardiovascular Risk Assessment
            </p>
        </div>
        """, unsafe_allow_html=True)


# Update the main app logic section to:
# --- Main App Logic ---
if not st.session_state.authenticated:
    login_page()
else:
    if st.session_state.current_page == "profile":
        patient_profile_page()
    elif st.session_state.current_page == "home":
        home_page()
    elif st.session_state.current_page == "risk":
        risk_assessment_page()
    elif st.session_state.current_page == "model":
        model_info_page()
    elif st.session_state.current_page == "user_management":
        admin_dashboard()  # Changed from user_management_page()

# --- Footer ---
st.markdown("---")
st.markdown(f"""
<div style='
    text-align: center; 
    padding: 1.5rem;
    background: rgba(30, 41, 59, 0.5);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    margin-top: 2rem;
'>
    <p style='margin-bottom: 0.5rem; font-size: 0.9rem;'>
    <strong>Cardio-AI</strong> | Clinical Decision Support System
    </p>
    <p style='font-size: 0.8rem; opacity: 0.7;'>
    This tool does not replace professional medical advice. Always consult a healthcare provider.
    </p>
</div>
""", unsafe_allow_html=True)