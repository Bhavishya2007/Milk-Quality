"""
🐄 Milk Quality Checker - Streamlit App 🐄
Making dairy testing adorable! ✨
"""

import streamlit as st
import joblib
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="🐄 Milk Quality Checker",
    page_icon="🐄",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for cute styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    }
    .title {
        text-align: center;
        color: #8b5a2b;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        color: #a0522d;
        font-style: italic;
    }
    .hint {
        color: #db7093;
        font-size: 0.9em;
    }
    .result-box {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: 20px;
    }
    .result-low {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        color: #2d5a27;
    }
    .result-medium {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #8b4513;
    }
    .result-high {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #8b0000;
    }
    .footer {
        text-align: center;
        color: #8b4513;
        margin-top: 30px;
    }
    .grade-emoji {
        font-size: 3em;
    }
</style>
""", unsafe_allow_html=True)

# Load the trained model
@st.cache_resource
def load_model():
    return joblib.load("milk_quality_model.pkl")

model = load_model()

# Grade mapping
grade_map = {0: 'low', 1: 'medium', 2: 'high'}
grade_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}
grade_names = {'low': 'LOW Quality', 'medium': 'MEDIUM Quality', 'high': 'HIGH Quality'}

# Title
st.markdown('<h1 class="title">🐄 Milk Quality Checker 🐄</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Making dairy testing adorable! ✨</p>', unsafe_allow_html=True)

st.write("")

# Create form
with st.container():
    st.markdown("### 🌸 Enter Milk Details 🌸")
    st.markdown('<p class="hint">💡 Hint: pH (3-10), Temp (20-90)</p>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        ph = st.number_input(
            "🧪 pH Level",
            min_value=3.0,
            max_value=10.0,
            value=6.6,
            step=0.1,
            help="Milk pH is typically between 6.5-6.8"
        )
        
        temperature = st.number_input(
            "🌡️ Temperature (°C)",
            min_value=20.0,
            max_value=90.0,
            value=35.0,
            help="Temperature in Celsius"
        )
        
        taste = st.selectbox(
            "👅 Taste",
            options=[("", "Select..."), (1, "Good (1)"), (0, "Bad (0)")],
            format_func=lambda x: x[1] if x else "Select..."
        )
        
        odor = st.selectbox(
            "👃 Odor",
            options=[("", "Select..."), (1, "Good (1)"), (0, "Bad (0)")],
            format_func=lambda x: x[1] if x else "Select..."
        )
    
    with col2:
        fat = st.selectbox(
            "🥛 Fat",
            options=[("", "Select..."), (1, "High (1)"), (0, "Low (0)")],
            format_func=lambda x: x[1] if x else "Select..."
        )
        
        turbidity = st.selectbox(
            "💧 Turbidity",
            options=[("", "Select..."), (1, "High (1)"), (0, "Low (0)")],
            format_func=lambda x: x[1] if x else "Select..."
        )
        
        colour = st.number_input(
            "🎨 Colour (240-255)",
            min_value=240,
            max_value=255,
            value=255,
            help="Colour value between 240-255"
        )

# Check if all fields are filled
all_filled = all([
    taste != "",
    odor != "",
    fat != "",
    turbidity != ""
])

# Predict button
if st.button("🔮 Predict Quality", type="primary"):
    if not all_filled:
        st.error("❌ Please fill in all the fields!")
    else:
        # Extract features
        features = [ph, temperature, 
                   taste[0] if isinstance(taste, tuple) else taste, 
                   odor[0] if isinstance(odor, tuple) else odor,
                   fat[0] if isinstance(fat, tuple) else fat,
                   turbidity[0] if isinstance(turbidity, tuple) else turbidity,
                   colour]
        
        # Make prediction
        prediction = model.predict([features])[0]
        probabilities = model.predict_proba([features])[0]
        confidence = max(probabilities)
        
        grade = grade_map[int(prediction)]
        
        # Display result
        st.markdown("### ✨ Prediction Result ✨")
        
        result_class = f"result-{grade}"
        emoji = grade_emoji[grade]
        
        st.markdown(f"""
        <div class="result-box {result_class}">
            <div class="grade-emoji">{emoji} {emoji} {emoji}</div>
            <h2>{grade_names[grade]}</h2>
            <p>Confidence: {(confidence * 100):.2f}% 💕</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown('<p class="footer">🐮 Made with love for milk lovers! 🐮</p>', unsafe_allow_html=True)

# Fun cow facts
with st.expander("🐄 Fun Cow Facts"):
    st.write("🐮 Cows have best friends and they get stressed when separated!")
    st.write("🥛 A cow produces an average of 6-8 gallons of milk per day!")
    st.write("👀 Cows have almost 360-degree panoramic vision!")

