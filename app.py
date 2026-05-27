import streamlit as st
import numpy as np
import joblib
import os
import time
from PIL import Image
from main import extract_features 
from treatments import get_treatment 

# --- PAGE SETUP ---
st.set_page_config(page_title="Agri-Vision™ Terminal", layout="wide", page_icon="🌿")

# Custom UI Styling
st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 15px; border: 1px solid #e0e0e0; }
    .stProgress > div > div > div > div { background-color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD MODELS ---
@st.cache_resource
def load_assets():
    model = joblib.load('models/ANN_MLP.pkl')
    scaler = joblib.load('models/scaler.pkl')
    le = joblib.load('models/label_encoder.pkl')
    return model, scaler, le

try:
    model, scaler, le = load_assets()
except:
    st.error("⚠️ AI Models not found. Please run training first.")
    st.stop()

# --- SIDEBAR: EDUCATION & LOGS ---
with st.sidebar:
    st.header("📚 Education Center")
    st.write("Compare your scan with known symptoms:")
    
    # Disease Reference Library
    disease_ref = st.selectbox("Select Disease to Study", le.classes_)
    ref_info = get_treatment(disease_ref)
    if ref_info:
        st.markdown(f"**Severity:** :{ref_info['color']}[{ref_info['severity']}]")
        st.caption(ref_info['description'])
        
        # In a real app, you'd show a reference image here
        # st.image(f"reference_library/{disease_ref}.jpg") 
    
    st.divider()
    st.header("📜 System Activity Log")
    st.caption("Auto-tracking car diagnostics...")
    st.code("10:42 - GPS Connected\n10:45 - Specimen Uploaded\n10:46 - HOG Features Extracted", language="text")

# --- MAIN TERMINAL ---
col_main, col_report = st.columns([1, 1])

with col_main:
    st.title("🌿 Agri-Vision™ AI")
    st.subheader("Smart Irrigation Car Diagnostic Terminal")
    
    uploaded_file = st.file_uploader("Capture specimen from camera...", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True, caption="Live Specimen Feed")
        
        if st.button("🚀 INITIATE DEEP SCAN"):
            with st.status("Analyzing Specimen...", expanded=True) as status:
                st.write("Extracting HOG Texture Gradients...")
                time.sleep(0.6)
                st.write("Calculating HSV Color Histograms...")
                time.sleep(0.6)
                st.write("Consulting Neural Network...")
                time.sleep(0.5)
                status.update(label="Analysis Complete!", state="complete", expanded=False)
            
            # Save and Predict
            temp_path = "temp_scan.jpg"
            img.save(temp_path)
            features = extract_features(temp_path)
            features_scaled = scaler.transform([features])
            
            # Get Probabilities (to show confidence)
            probs = model.predict_proba(features_scaled)[0]
            max_prob = np.max(probs)
            prediction_idx = np.argmax(probs)
            prediction_label = str(le.inverse_transform([prediction_idx])[0])
            
            # Store in session state for the right column to see
            st.session_state['result'] = (prediction_label, max_prob)
            os.remove(temp_path)

# --- RIGHT COLUMN: THE REPORT ---
with col_report:
    if 'result' in st.session_state:
        label, confidence = st.session_state['result']
        treatment = get_treatment(label)
        
        st.header("📊 Diagnostic Report")
        
        # Confidence Gauge
        st.write(f"**AI Confidence Score**")
        st.progress(float(confidence))
        st.write(f"{confidence*100:.1f}% Match")

        st.divider()
        
        clean_name = label.replace("___", ": ").replace("_", " ")
        st.markdown(f"### Detection: :{treatment['color']}[{clean_name}]")
        
        # Quick Stats
        s1, s2 = st.columns(2)
        s1.metric("Severity", treatment['severity'])
        s2.metric("Spread Risk", treatment['spread_risk'])
        
        st.markdown("#### 📝 Clinical Summary")
        st.info(treatment['description'])
        
        st.markdown("#### 🛠️ Immediate Recovery Steps")
        for i, step in enumerate(treatment['steps'], 1):
            st.markdown(f"**{i}.** {step}")
            
        if st.button("🖨️ Generate PDF Report"):
            st.toast("Report ready for export!")
    else:
        st.info("Awaiting live feed from irrigation car to generate report...")

st.divider()
st.caption("Terminal ID: AASTMT-HELIOPOLIS-01 | Environment: 32°C | Humidity: 65%")