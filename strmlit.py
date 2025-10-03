import streamlit as st
import numpy as np
import pandas as pd
import joblib
import matplotlib.pyplot as plt

# Load trained model and scaler
best_model = joblib.load(r"C:\Users\gamin\Documents\Finalyearproj\best_model (2).pkl")
scaler = joblib.load(r"C:\Users\gamin\Documents\Finalyearproj\scaler (1).pkl")

# Define correct feature names based on training data
feature_names = ['Age', 'Gender', 'BMI', 'Chol', 'TG', 'HDL', 'LDL']

def predict_heart_disease(input_data):
    """Predict heart disease based on input data."""
    input_df = pd.DataFrame([input_data], columns=feature_names)
    input_scaled = scaler.transform(input_df)
    prediction = best_model.predict_proba(input_scaled)[0]
    return prediction

# Streamlit UI
st.set_page_config(page_title="CardioML", layout="wide", initial_sidebar_state="collapsed", page_icon="🩺")

# Initialize session state for navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# Sidebar for navigation (Ensures same-tab rendering)
with st.sidebar:
    st.title("🔹 Navigation")
    if st.button("🏠 Home"):
        st.session_state.current_page = "home"
    if st.button("❤️ About Heart Disease"):
        st.session_state.current_page = "about"
    if st.button("📊 Best Model"):
        st.session_state.current_page = "model"

# Display the selected page
if st.session_state.current_page == "home":
    st.title("🩺 Heart Disease Prediction")
    st.write("Enter patient details to predict heart disease risk.")

    # Input fields
age = st.number_input("Enter Age", min_value=1, max_value=120, value=45)
sex = st.selectbox("Gender", ["Female", "Male"])
gender = 1 if sex == "Male" else 0
bmi = st.number_input("Enter BMI", min_value=10.0, max_value=50.0, value=25.0)
chol = st.number_input("Enter Cholesterol Level (Chol)", min_value=100, max_value=300, value=200)
tg = st.number_input("Enter Triglycerides (TG)", min_value=50, max_value=500, value=150)
hdl = st.number_input("Enter HDL Cholesterol", min_value=20, max_value=100, value=50)
ldl = st.number_input("Enter LDL Cholesterol", min_value=50, max_value=250, value=130)

# Predict button
if st.button("🔍 Predict Heart Disease"):
    try:
        input_data = [float(age), gender, float(bmi), float(chol), float(tg), float(hdl), float(ldl)]
        prediction = predict_heart_disease(input_data)
        high_risk = prediction[1] * 100
        low_risk = prediction[0] * 100
        
        # Display result
        risk_label = "High Risk" if high_risk > 50 else "Low Risk"
        color_class = "critical" if high_risk > 50 else "success"
        
        st.markdown(f"""<div class='highlight-box {color_class}'>
                    <h2 style='font-size:26px;'>{risk_label}</h2>
                    <p style='font-size:23px;'><strong>Confidence Score:</strong> {high_risk:.2f}%</p>
                    </div>""", unsafe_allow_html=True)
        
        if high_risk > 50:
            st.markdown("""<div class='highlight-box warning' style='font-size:22px;'>⚠️ Your heart health might be at risk. Please consult a doctor.</div>""", unsafe_allow_html=True)
            st.markdown("### Recommendations:")
            st.markdown("- 🏥 Consult a cardiologist immediately.")
            st.markdown("- 🥗 Adopt a heart-healthy diet with low cholesterol and saturated fats.")
            st.markdown("- 🏃 Engage in regular physical activity and maintain a healthy weight.")
            st.markdown("- 💓 Monitor your blood pressure and cholesterol levels regularly.")
        else:
            st.markdown("""<div class='highlight-box success' style='font-size:22px;'>✔️ Your heart health seems normal. Maintain a healthy lifestyle!</div>""", unsafe_allow_html=True)
            st.markdown("### Recommendations:")
            st.markdown("- 🍎 Continue maintaining a balanced diet rich in fruits and vegetables.")
            st.markdown("- 🏋️ Exercise regularly to keep your heart strong.")
            st.markdown("- 😌 Keep stress levels in check and maintain a healthy routine.")
        
        # Visualization
        fig, ax = plt.subplots(figsize=(6,4))
        ax.bar(["High Risk", "Low Risk"], [high_risk, low_risk], color=["#D32F2F", "#66BB6A"], edgecolor="black")
        ax.set_ylabel("Confidence (%)")
        ax.set_xlabel("Heart Disease Risk")
        ax.set_title("Risk Visualization (%)")
        ax.set_ylim(0, 100)
        for i, v in enumerate([high_risk, low_risk]):
            ax.text(i, v + 2, f"{v:.2f}%", ha='center', fontsize=12, fontweight='bold')
        
        st.pyplot(fig)
    except ValueError:
        st.error("❌ Please enter valid numerical values for all fields.")

elif st.session_state.current_page == "about":
    st.title("💖 About Heart Disease & Its Types")
    st.write("""
    Heart disease refers to a range of conditions that affect the heart's structure and function. 
    It is a leading cause of death worldwide but can often be prevented through lifestyle changes and medical care.
    """)

    st.subheader("🩺 Common Types of Heart Disease")
    st.markdown("""
    - **Coronary Artery Disease (CAD):** Plaque buildup in arteries.
    - **Heart Failure:** The heart fails to pump efficiently.
    - **Arrhythmias:** Irregular heartbeat.
    - **Congenital Heart Defects (CHD):** Present from birth.
    - **Hypertensive Heart Disease:** Due to high blood pressure.
    - **Cardiomyopathy:** Weakening of heart muscle.
    - **Valvular Heart Disease:** Damage to heart valves.""")
    
    st.subheader("⚠️ Common Symptoms of Heart Disease")
    st.markdown("""
    - **Chest pain or discomfort (angina).**
    - **Shortness of breath.**
    - **Dizziness or lightheadedness.**
    - **Fatigue or weakness.**
    - **Swelling in the legs, ankles, or feet.**
    - **Irregular heartbeat or palpitations.**
    - **Nausea, cold sweat, or indigestion (especially in women).**""")

elif st.session_state.current_page == "model":
    st.title("📊 Best Model: Random Forest")

    st.markdown("""
    Our Heart Disease Prediction system uses **Random Forest**, which achieved the best results compared to other models.  
    **Why Random Forest?**
    
    - ✅ **High Accuracy (89.5%)**
    - ✅ **Handles Non-Linear Patterns**
    - ✅ **Prevents Overfitting**
    - ✅ **Feature Importance Analysis**
    """)

    st.subheader("📈 Performance Metrics:")
    st.markdown("""
    - **Accuracy:** 89.5%  
    - **Precision:** 88.2%  
    - **Recall:** 90.1%  
    - **F1 Score:** 89.1%  
    """)

    st.subheader("📌 Why Not Other Models?")
    st.markdown("""
    - ❌ Logistic Regression: Too simple for complex patterns.  
    - ❌ SVM: Computationally expensive.  
    - ❌ Neural Networks: Overkill for small tabular datasets.  
    """)

