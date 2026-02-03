import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import sys
from pathlib import Path


from knowledge_base import get_personalized_advice

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Air Quality Guardian",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem;}
    
    .app-header {text-align: center; color: white; padding: 2rem 0; margin-bottom: 2rem;}
    .app-title {font-size: 3.5rem; font-weight: 800; margin: 0;}
    .app-subtitle {font-size: 1.2rem; opacity: 0.9; margin-top: 0.5rem;}
    
    .card {background: white; border-radius: 20px; padding: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.2); margin: 1rem 0;}
    
    .status-good {background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; font-size: 1.5rem; font-weight: 700; box-shadow: 0 8px 20px rgba(17,153,142,0.3);}
    .status-moderate {background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; font-size: 1.5rem; font-weight: 700; box-shadow: 0 8px 20px rgba(245,87,108,0.3);}
    .status-unhealthy {background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 2rem; border-radius: 15px; text-align: center; font-size: 1.5rem; font-weight: 700; box-shadow: 0 8px 20px rgba(250,112,154,0.3);}
    
    .big-number {font-size: 4rem; font-weight: 800; color: #667eea; margin: 1rem 0;}
    .metric-label {font-size: 1rem; color: #666; text-transform: uppercase; letter-spacing: 2px;}
    
    .input-section {background: rgba(255,255,255,0.95); border-radius: 15px; padding: 1.5rem; margin: 1rem 0;}
    .section-title {font-size: 1.5rem; font-weight: 700; color: #667eea; margin-bottom: 1rem;}
    
    .rag-card {background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 5px 15px rgba(0,0,0,0.1);}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="app-header">
    <div class="app-title">🌍 Air Guardian</div>
    <div class="app-subtitle">Know Your Air. Breathe Better. • Chemnitz, Germany</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# API INTEGRATION
# ============================================================
def get_forecast(inputs):
    try:
        resp = requests.post("http://localhost:8000/forecast", json=inputs, timeout=5)
        return resp.json()
    except Exception as e:
        st.error(f"⚠️ API Error: {str(e)}")
        return None

# ============================================================
# GET CURRENT PM10
# ============================================================
@st.cache_data(ttl=300)
def get_current_pm10():
    try:
        df = pd.read_csv("../data/processed/chemnitz_features.csv")
        return float(df['pm10'].iloc[-1])
    except:
        return 25.0

current_pm10 = get_current_pm10()

# ============================================================
# USER INPUTS
# ============================================================
with st.container():
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🌤️ Tell us about the weather</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🌡️ How warm is it?**")
        temp = st.select_slider(
            "Temperature",
            options=["Very Cold", "Cold", "Cool", "Mild", "Warm", "Hot"],
            value="Cool",
            label_visibility="collapsed"
        )
        temp_map = {"Very Cold": -5, "Cold": 2, "Cool": 8, "Mild": 15, "Warm": 22, "Hot": 30}
        temp_c = temp_map[temp]
        st.caption(f"({temp_c}°C)")
    
    with col2:
        st.markdown("**💨 How windy?**")
        wind = st.select_slider(
            "Wind",
            options=["Calm", "Light Breeze", "Breezy", "Windy", "Very Windy"],
            value="Light Breeze",
            label_visibility="collapsed"
        )
        wind_map = {"Calm": 0.5, "Light Breeze": 2, "Breezy": 4, "Windy": 7, "Very Windy": 12}
        wind_ms = wind_map[wind]
        st.caption(f"({wind_ms} m/s)")
    
    with col3:
        st.markdown("**☁️ How humid/cloudy?**")
        humidity = st.select_slider(
            "Humidity",
            options=["Dry", "Normal", "Humid", "Very Humid"],
            value="Normal",
            label_visibility="collapsed"
        )
        humidity_map = {"Dry": 40, "Normal": 65, "Humid": 80, "Very Humid": 95}
        humidity_pct = humidity_map[humidity]
        st.caption(f"({humidity_pct}%)")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Time input
with st.container():
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">⏰ What time is it?</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        hour = st.slider("Select hour", 0, 23, datetime.now().hour, format="%d:00", label_visibility="collapsed")
    with col2:
        st.markdown(f"**Selected: {hour}:00**")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PREDICT BUTTON
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔮 **CHECK AIR QUALITY NOW**", type="primary", use_container_width=True):
    
    # Build real inputs
    inputs = {
        "hour": hour,
        "latest_pm10": current_pm10,
        "temp": temp_c,
        "humidity": humidity_pct,
        "wind_speed": wind_ms,
        "precipitation": 0.0
    }
    
    # API CALL
    forecast = get_forecast(inputs)
    
    if forecast:
        pm10_forecast = forecast['pm10_forecast_1h']
        
        # ============================================================
        # RESULTS
        # ============================================================
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Right Now</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="big-number">{current_pm10:.0f}</div>', unsafe_allow_html=True)
            st.markdown("**PM10 Level** • Live sensor reading", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Next Hour Forecast</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="big-number">{pm10_forecast:.0f}</div>', unsafe_allow_html=True)
            change = pm10_forecast - current_pm10
            st.markdown(f"**PM10 Level** • {change:+.0f} predicted change", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Health advice
        st.markdown("<br>", unsafe_allow_html=True)
        
        if pm10_forecast < 25:
            st.markdown("""
            <div class="status-good">
                ✅ EXCELLENT AIR QUALITY<br>
                <span style="font-size:1rem; font-weight:400;">
                Perfect for outdoor activities • Safe for everyone • Enjoy nature!
                </span>
            </div>
            """, unsafe_allow_html=True)
            
        elif pm10_forecast < 50:
            st.markdown("""
            <div class="status-moderate">
                ℹ️ GOOD AIR - MINOR CAUTION<br>
                <span style="font-size:1rem; font-weight:400;">
                Safe for most people • Sensitive groups: take it easy
                </span>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.markdown("""
            <div class="status-unhealthy">
                ⚠️ ELEVATED POLLUTION<br>
                <span style="font-size:1rem; font-weight:400;">
                Limit outdoor time • Sensitive groups stay inside
                </span>
            </div>
            """, unsafe_allow_html=True)
        
        # Gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pm10_forecast,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"PM10 Forecast ({hour}:00)", 'font': {'size': 20}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 25], 'color': "#38ef7d"},
                    {'range': [25, 50], 'color': "#f5576c"},
                    {'range': [50, 100], 'color': "#fa709a"}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 50}
            }
        ))
        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        # ============================================================
        # RAG HEALTH ASSISTANT
        # ============================================================
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🩺 **Personalized Health Assistant**")
        st.markdown("*Powered by WHO & EU Air Quality Guidelines*")
        
        # User profile selection
        col1, col2 = st.columns([1, 2])
        with col1:
            user_profile = st.selectbox(
                "Who's asking?",
                ["general", "children", "elderly", "asthma", "heart_disease", "pregnant"],
                format_func=lambda x: {
                    "general": "👤 General public",
                    "children": "👶 Child (under 12)",
                    "elderly": "👴 Elderly (65+)",
                    "asthma": "😷 Asthma/respiratory",
                    "heart_disease": "❤️ Heart condition",
                    "pregnant": "🤰 Pregnant"
                }[x]
            )
        
        with col2:
            st.info(f"🎯 Getting personalized advice for: **{user_profile.replace('_', ' ').title()}**")
        
        # Get RAG advice
        rag_advice = get_personalized_advice(pm10_forecast, user_profile)
        
        # Display personalized card
        st.markdown('<div class="rag-card">', unsafe_allow_html=True)
        
        st.markdown(f"#### 📊 Air Quality Level: **{rag_advice['category']}** ({rag_advice['pm10_level']} µg/m³)")
        st.markdown(f"**General Advice:** {rag_advice['general_advice']}")
        
        # Profile-specific advice
        if "profile_specific" in rag_advice:
            st.warning(f"**⚠️ Why you should care:** {rag_advice['profile_specific']['why_vulnerable']}")
            st.success(f"**🛡️ Your precautions:** {rag_advice['profile_specific']['precautions']}")
        
        # Activities
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**✅ You can:**")
            for activity in rag_advice['recommended_activities'][:3]:
                st.markdown(f"• {activity}")
        
        with col2:
            st.markdown("**👥 Sensitive groups:**")
            st.markdown(rag_advice['sensitive_groups_advice'])
        
        # Mitigation strategies
        if "mitigation" in rag_advice:
            with st.expander("🛠️ How to Protect Yourself"):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**🏠 Indoors:**")
                    for tip in rag_advice['mitigation']['indoor']:
                        st.markdown(f"• {tip}")
                with col2:
                    st.markdown("**🚶 Outdoors:**")
                    for tip in rag_advice['mitigation']['outdoor']:
                        st.markdown(f"• {tip}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Technical details
        with st.expander("🔍 Technical Details"):
            st.json({
                "Inputs": inputs,
                "Model Output": forecast,
                "RAG Profile": user_profile,
                "Health Category": rag_advice['category']
            })

# ============================================================
# FOOTER
# ============================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align:center; color:white; opacity:0.7; font-size:0.9rem;">
    📡 Powered by Chemnitz Sensor 11057 • 🤖 XGBoost AI (R²=0.65) • 🩺 WHO Guidelines RAG<br>
    Live predictions • Updates hourly • Personalized health advice
</div>
""", unsafe_allow_html=True)
