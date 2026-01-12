import streamlit as st
import requests
import pandas as pd
from deep_translator import GoogleTranslator

# 1. Page Config
st.set_page_config(page_title="Weather Pro Max", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- Translations ---
texts = {
    "EN": {
        "title": "⚡ Weather Pro Max ⚡", "search_place": "Search City or Village...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind Speed", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒", 
        "alert_rain": "⚠️ STORM ALERT: Rain in 24h!",
        "warn_search": "Warn: search location first!"
    },
    "AR": {
        "title": "⚡ وذر برو ماكس ⚡", "search_place": "ابحث عن قرية أو مدينة...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق على أمازون 🛒",
        "alert_rain": "⚠️ تنبيه عاصفة: أمطار قادمة!",
        "warn_search": "تنبيه: ابحث عن مكان أولاً!"
    }
}
T = texts[st.session_state.lang]

# --- Functions ---
@st.cache_data(ttl=3600)
def get_coordinates(location_name, target_lang):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
        res = requests.get(url, headers={'User-Agent': 'WeatherApp_2026'}).json()
        if res:
            lat, lon = float(res[0]['lat']), float(res[0]['lon'])
            dest_lang = 'en' if target_lang == "EN" else 'ar'
            display_name = GoogleTranslator(source='auto', target=dest_lang).translate(res[0]['display_name'])
            return lat, lon, display_name
        return None, None, None
    except: return None, None, None

@st.cache_data(ttl=600)
def get_forecast(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        return requests.get(url).json()
    except: return None

# --- Extreme Gaming UI CSS ---
def apply_gaming_ui(condition, temp):
    # Dynamic Colors based on weather
    accent_color = "#00f2ff" if "rain" in condition else "#ff00ff" if temp > 28 else "#00ff88"
    bg_base = "#0f172a" # Deep Dark Blue/Black
    
    st.markdown(f"""
        <style>
        /* Base Styling */
        .stApp {{
            background-color: {bg_base} !important;
            background-image: radial-gradient(circle at 50% 50%, {accent_color}11 0%, transparent 80%) !important;
            color: white !important;
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }}
        
        /* Neon Search Box */
        .stTextInput input {{
            background: rgba(255,255,255,0.05) !important;
            border: 1px solid {accent_color}55 !important;
            border-radius: 15px !important;
            color: white !important;
            box-shadow: 0 0 15px {accent_color}22;
        }}

        /* Gaming Metric Cards */
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(20px);
            border-radius: 20px !important;
            padding: 25px !important;
            border: 1px solid {accent_color}44 !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8), inset 0 0 15px {accent_color}11 !important;
            text-align: center !important;
        }}
        [data-testid="stMetricValue"] {{ 
            font-size: 2.8rem !important; 
            font-weight: 800 !important; 
            color: {accent_color} !important;
            text-shadow: 0 0 20px {accent_color}aa;
            justify-content: center !important;
        }}
        [data-testid="stMetricLabel"] {{ 
            text-transform: uppercase; 
            letter-spacing: 2px; 
            color: #888 !important;
            justify-content: center !important;
        }}

        /* Glow Buttons */
        .stButton button {{
            background: linear-gradient(45deg, {accent_color}, #6366f1) !important;
            border: none !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 12px !important;
            box-shadow: 0 0 20px {accent_color}44 !important;
            transition: 0.3s !important;
        }}
        .stButton button:hover {{ transform: scale(1.05); box-shadow: 0 0 30px {accent_color}77 !important; }}

        /* Rain/Weather Overlay */
        .weather-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1; pointer-events: none;
            background: url('https://www.transparenttextures.com/patterns/stardust.png');
            opacity: 0.3;
        }}
        
        .alert-neon {{
            border: 2px solid #ff0055;
            background: rgba(255, 0, 85, 0.1);
            color: #ff0055;
            padding: 15px; border-radius: 15px;
            text-align: center; font-weight: bold;
            text-shadow: 0 0 10px #ff0055;
            box-shadow: 0 0 20px #ff005533;
            margin-bottom: 20px;
        }}

        .amazon-card {{
            background: rgba(255,255,255,0.95);
            color: #111;
            padding: 20px; border-radius: 25px;
            text-align: center; margin-top: 50px;
            border-bottom: 8px solid #ff9900;
            box-shadow: 0 0 40px rgba(0,0,0,0.5);
        }}
        </style>
        <div class="weather-overlay"></div>
    """, unsafe_allow_html=True)

# --- App Logic ---
header_col1, header_col2 = st.columns([9, 1])
with header_col1: st.markdown(f"<h1 style='text-align: left; text-shadow: 0 0 20px #6366f1;'>{T['title']}</h1>", unsafe_allow_html=True)
with header_col2: 
    if st.button("🌐"):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

query = st.text_input("📍", placeholder=T["search_place"])
btn_col1, btn_col2, btn_col3 = st.columns([1,1.5,1])
with btn_col2: analyze_click = st.button(T["btn_analyze"], use_container_width=True)

if query:
    lat, lon, name = get_coordinates(query, st.session_state.lang)
    if lat:
        forecast = get_forecast(lat, lon)
        if forecast:
            curr = forecast['list'][0]
            cond, temp = curr['weather'][0]['main'].lower(), curr['main']['temp']
            apply_gaming_ui(cond, temp)
            
            will_rain = any("rain" in f['weather'][0]['main'].lower() for f in forecast['list'][:8])
            if will_rain: st.markdown(f'<div class="alert-neon">{T["alert_rain"]}</div>', unsafe_allow_html=True)
            
            st.markdown(f"<h2 style='text-align:center;'>{name}</h2>", unsafe_allow_html=True)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{temp}°C")
            m2.metric(T["clouds"], f"{curr['clouds']['all']}%")
            m3.metric(T["wind"], f"{curr['wind']['speed']} m/s")
            m4.metric(T["humidity"], f"{curr['main']['humidity']}%")

            if analyze_click:
                st.markdown("<div style='background:rgba(255,255,255,0.05); padding:20px; border-radius:20px; border:1px solid rgba(255,255,255,0.1); margin-top:20px;'>", unsafe_allow_html=True)
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12)
                st.markdown("</div>", unsafe_allow_html=True)

            p_cat = "umbrella" if will_rain else "sunglasses" if temp > 28 else "winter+jacket"
            st.markdown(f"<p style='text-align:center; opacity:0.4; margin-top:60px;'>Created by: Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
            st.markdown(f"""<div class="amazon-card">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="80"><br>
                <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold; font-size:1.2rem;">{T['shop']}</a>
            </div>""", unsafe_allow_html=True)
    else: st.error("Target missing!")
else:
    apply_gaming_ui("clear", 25)
    if analyze_click: st.warning(T["warn_search"])
