import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

# --- Logic: Search Engine (Force English Results) ---
@st.cache_data(ttl=3600)
def get_coordinates(location_name):
    try:
        # Translate input to English for the engine
        translated_input = GoogleTranslator(source='auto', target='en').translate(location_name)
        url = f"https://nominatim.openstreetmap.org/search?q={translated_input}&format=json&limit=1&accept-language=en"
        headers = {'User-Agent': 'WeatherApp_2026'}
        res = requests.get(url, headers=headers, timeout=10).json()
        if res:
            # Get the display name and make sure it's English
            raw_name = res[0]['display_name']
            english_name = GoogleTranslator(source='auto', target='en').translate(raw_name)
            return float(res[0]['lat']), float(res[0]['lon']), english_name
        return None, None, None
    except: return None, None, None

@st.cache_data(ttl=600)
def get_weather_by_coords(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- Visual Effects ---
def apply_visuals(condition="clear", temp=25):
    bg = "linear-gradient(to bottom, #1e3c72, #2a5298)"
    if "rain" in condition: bg = "linear-gradient(to bottom, #203a43, #2c5364)"
    elif temp > 28: bg = "linear-gradient(135deg, #FF8C00 0%, #FFD700 100%)"
    
    st.markdown(f"""
        <style>
        .stApp {{ background: {bg}; transition: all 1s ease; color: white; }}
        [data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(5px); border-radius: 12px; }}
        .main-card {{ background: rgba(0, 0, 0, 0.3); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); }}
        .amazon-footer {{ background: white; color: #232f3e; padding: 15px; border-radius: 15px; text-align: center; margin-top: 50px; border-bottom: 5px solid #ff9900; max-width: 500px; margin: 0 auto; }}
        </style>
        """, unsafe_allow_html=True)

# --- App Structure ---
st.markdown("<h1 style='text-align: center;'>🌤️ Weather Pro Max</h1>", unsafe_allow_html=True)

# The Search Box
search_query = st.text_input("📍 Location Search:", placeholder="Enter city or village...")

# The Button (Always Present)
col1, col2, col3 = st.columns([1,1,1])
with col2:
    analyze_click = st.button("Explore Local Analysis & Map", use_container_width=True)

# App Logic
if search_query:
    lat, lon, display_name = get_coordinates(search_query)
    
    if lat:
        weather = get_weather_by_coords(lat, lon)
        if weather:
            cond = weather['weather'][0]['main'].lower()
            temp = weather['main']['temp']
            apply_visuals(cond, temp)

            # Animation
            anim_urls = {"rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
                         "clear": "https://lottie.host/a8a5b293-61a7-47_b8-80f2-b892a4066c0d/Y08T7N1p5N.json"}
            anim = load_lottieurl(anim_urls.get(cond, "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json"))
            if anim: st_lottie(anim, height=180, key="weather_anim")

            st.markdown(f"<h3 style='text-align:center;'>{display_name}</h3>", unsafe_allow_html=True)

            if analyze_click:
                st.markdown("<div class='main-card'>", unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Temperature", f"{temp}°C")
                m2.metric("Clouds", f"{weather['clouds']['all']}%")
                m3.metric("Wind", f"{weather['wind']['speed']} m/s")
                m4.metric("Humidity", f"{weather['main']['humidity']}%")
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=11)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error("Location not found. Check spelling.")
else:
    apply_visuals()
    if analyze_click:
        st.warning("Please enter a location first to see the analysis!")

# Amazon Recommendation Logic
p_cat = "sunglasses" # Default
if search_query and 'weather' in locals():
    if temp < 15: p_cat = "winter+coat"
    elif "rain" in cond: p_cat = "umbrella"

# Global Footer
st.markdown(f"<br><br><center style='color:white; opacity:0.6;'>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
st.markdown(f"""
    <div class="amazon-footer">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="70"><br>
        <p style="margin:5px 0; font-weight:bold;">Weather Recommendation:</p>
        <p>Stay prepared! Shop top-rated products for this weather.</p>
        <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold;">View Deals on Amazon 🛒</a>
    </div>
""", unsafe_allow_html=True)
