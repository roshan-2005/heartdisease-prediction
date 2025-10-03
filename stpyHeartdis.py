import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# Streamlit App UI
st.set_page_config(page_title="Heart Disease Prediction", page_icon="🩺", layout="centered")

st.markdown("""
    <style>
    .high-risk {
        background-color:rgb(176, 87, 87);
        color:rgb(211, 47, 47);
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 5px;
    }
    .low-risk {
        background-color:rgb(27, 114, 55);
        color:rgb(255, 255, 255);
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        padding: 10px;
        border-radius: 5px;
    }
    .confidence {
        font-size: 18px;
        text-align: center;
        font-weight: bold;
        color: #5E35B1;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Heart Disease Prediction System")
st.write("Enter your clinical data below to predict the risk of heart disease.")

# User Input Form
with st.form(key="input_form"):
    age = st.number_input("Age", min_value=1, max_value=100, step=1, key="age")
    gender = st.selectbox("Gender", ["Male", "Female"], key="gender")
    chol = st.number_input("Cholesterol Level (mg/dL)", min_value=50, max_value=500, step=1, key="chol")
    hdl = st.number_input("High-Density Lipoprotein (HDL) Level (mg/dL)", min_value=10, max_value=150, step=1, key="hdl")
    ldl = st.number_input("Low-Density Lipoprotein (LDL) Level (mg/dL)", min_value=10, max_value=300, step=1, key="ldl")
    bun = st.number_input("Blood Urea Nitrogen (BUN) Level (mg/dL)", min_value=100, max_value=500, step=1, key="bun")
    
    submit_button = st.form_submit_button(label="Predict")

# Convert categorical inputs to numerical values
gender = 1 if gender == "Male" else 0

# Simulating a model prediction (Replace with actual ML model later)
def predict_heart_disease(features):
    chol, hdl, ldl, bun = features[0][2], features[0][3], features[0][4], features[0][5]  # Extract values
    risk_score = np.mean([chol, ldl, bun]) - hdl  # HDL is protective, so we subtract it
    prediction = "High Risk of Heart Disease" if risk_score > 150 else "Low Risk"
    
    # Confidence Calculation
    if risk_score > 200:
        confidence = 50  # Capped for very high-risk cases
    elif risk_score > 180:
        confidence = 60
    elif risk_score > 150:
        confidence = 70
    elif risk_score > 120:
        confidence = 80
    else:
        confidence = 90  # Higher confidence for low risk

    return prediction, confidence

if submit_button:
    user_data = np.array([[age, gender, chol, hdl, ldl, bun]])
    prediction, confidence = predict_heart_disease(user_data)

    # Display results with different styling for risk levels
    if prediction == "High Risk of Heart Disease":
        st.markdown(f"<div class='high-risk'>{prediction}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='low-risk'>{prediction}</div>", unsafe_allow_html=True)
    
    st.markdown(f"<div class='confidence'>Confidence Score: {confidence:.2f}%</div>", unsafe_allow_html=True)

    # Additional Health Advice
    if prediction == "High Risk of Heart Disease":
        st.warning("⚠️ Please consult a healthcare provider for further evaluation.")
    else:
        st.success("✅ Your heart health seems normal. Maintain a healthy lifestyle!")

    # Correct Risk Visualization
    fig, ax = plt.subplots()
    labels = ['High Risk', 'Low Risk']
    values = [confidence if prediction == "High Risk of Heart Disease" else 100 - confidence, 
              100 - confidence if prediction == "High Risk of Heart Disease" else confidence]

    colors = ['red', 'lightgreen']  # High Risk = Red, Low Risk = Green

    bars = ax.bar(labels, values, color=colors)
    ax.set_title("Risk Visualization (%)", fontsize=16, fontweight='bold')
    ax.set_xlabel("Heart Disease Risk", fontsize=12)
    ax.set_ylabel("Confidence (%)", fontsize=12)
    ax.set_ylim(0, 100)  # Ensure the graph is scaled correctly
    ax.bar_label(bars, fmt="%.2f%%")  # Show percentages on bars

    st.pyplot(fig)
