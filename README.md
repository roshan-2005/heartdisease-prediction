❤️ Cardio-AI

AI-Powered Heart Disease Risk Prediction System
Cardio-AI is an intelligent web application that predicts the risk of heart disease using machine learning. Built with a focus on real-world usability, it analyzes key health parameters and provides instant, actionable insights through an interactive interface.

🚀 Features

🧠 ML-Powered Prediction (Random Forest – 89.5% accuracy)
📊 Interactive Risk Visualization (Plotly charts)
🧾 Downloadable PDF Health Reports
🔐 User Authentication & Profile Management
🎨 Modern Glassmorphism UI (Streamlit)
⚡ Real-Time Prediction & Feedback
🧪 Input Parameters

The model evaluates the following health metrics:

Age
Gender
BMI
Cholesterol Level (Chol)
Triglycerides (TG)
HDL Cholesterol
LDL Cholesterol\

🛠️ Tech Stack

Frontend:
Streamlit
HTML/CSS (custom styling)

Backend & ML:
Python
Scikit-learn (Random Forest)
Pandas, NumPy

Visualization:
Plotly

Database:
MySQL

🧠 How It Works

User enters health data via UI
Data is preprocessed and validated
Random Forest model predicts risk level
Results are visualized with insights
Optional PDF report is generated

⚙️ Installation & Setup
# Clone the repository
git clone https://github.com/your-username/cardio-ai.git

# Navigate to project folder
cd cardio-ai

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run main.py
📂 Project Structure
├── main.py  
├── model/  
├── utils/  
├── static/  
├── database/  
└── requirements.txt  

📈 Model Performance
Algorithm: Random Forest
Accuracy: 89.5%
Optimized with feature selection & tuning

🔮 Future Enhancements

Wearable device integration
Multi-disease prediction (Heart, Liver, Kidney)
Advanced analytics dashboard
Personalized health recommendations
Mobile app version
