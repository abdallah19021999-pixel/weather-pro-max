import streamlit as st
import requests
import pandas as pd
from deep_translator import GoogleTranslator

# 1. Page Config
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- Translations ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Search city or village...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind Speed", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒", "alert_rain": "⚠️ Rain expected soon!"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "ابحث عن مدينة أو قرية...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق على أمازون 🛒", "alert_rain": "⚠️ أمطار متوقعة قريباً!"
    }
}
T = texts[st.session_state.lang]

# --- Logic Functions ---
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

# --- Advanced Elden Ring Atmosphere CSS ---
def apply_elden_style(condition, temp):
    # اختيار نوع التأثير بناءً على الجو
    if "rain" in condition:
        particle_color, particle_speed = "#4facfe", "1s" # مطر
    elif "snow" in condition or temp < 5:
        particle_color, particle_speed = "#ffffff", "5s" # ثلج
    else:
        particle_color, particle_speed = "#ffcc33", "8s" # رماد/غبار ذهبي (Elden Style)

    st.markdown(f"""
        <style>
        .stApp {{ background: #0a0a0b !important; color: white !important; }}
        
        /* طبقة الجرافيكس المتحركة في الخلفية */
        .atmosphere {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1; pointer-events: none;
            background: radial-gradient(circle at 50% 50%, #1a1a1c, #000);
            overflow: hidden;
        }}
        .particle {{
            position: absolute; background: {particle_color};
            width: 2px; height: 15px; opacity: 0.3;
            animation: fall {particle_speed} linear infinite;
        }}
        @keyframes fall {{
            from {{ transform: translateY(-10vh) translateX(0); }}
            to {{ transform: translateY(110vh) translateX(20px); }}
        }}

        /* صندوق البحث - واضح جداً */
        .stTextInput input {{
            background: white !important; color: #111 !important;
            border-radius: 12px !important; padding: 12px !important;
            border: 3px solid #333 !important; font-size: 1.1rem !important;
        }}

        /* المقاييس - موسطة ومنظمة */
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.03) !important;
            backdrop-filter: blur(10px); border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.05); text-align: center !important;
        }}
        [data-testid="stMetricValue"] {{ 
            color: {particle_color} !important; font-size: 2.5rem !important;
            text-shadow: 0 0 15px {particle_color}55; justify-content: center !important;
        }}
        [data-testid="stMetricLabel"] {{ justify-content: center !important; color: #777 !important; }}

        /* الزرار الثابت */
        .stButton button {{
            background: #222 !important; color: gold !important;
            border: 1px solid gold !important; border-radius: 10px !important;
            font-weight: bold !important; width: 100%;
        }}
        .stButton button:hover {{ background: gold !important; color: black !important; }}

        .amazon-footer {{
            background: white; color: #111; padding: 20px; border-radius: 20px;
            text-align: center; margin-top: 50px; border-bottom: 5px solid #ff9900;
        }}
        </style>
        <div class="atmosphere">
            {" ".join([f'<div class="particle" style="left:{i*5}%; animation-delay:{i*0.2}s"></div>' for i in range(20)])}
        </div>
    """, unsafe_allow_html=True)

# --- UI Structure ---
h1, h2 = st.columns([9, 1])
with h1: st.title(T["title"])
with h2: 
    if st.button("🌐"):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

query = st.text_input("📍", placeholder=T["search_place"])
b1, b2, b3 = st.columns([1, 1.5, 1])
with b2: analyze = st.button(T["btn_analyze"])

if query:
    lat, lon, name = get_coordinates(query, st.session_state.lang)
    if lat:
        f = get_forecast(lat, lon)
        if f:
            curr = f['list'][0]
            cond, temp = curr['weather'][0]['main'].lower(), curr['main']['temp']
            apply_elden_style(cond, temp)
            
            if any("rain" in x['weather'][0]['main'].lower() for x in f['list'][:8]):
                st.warning(T["alert_rain"])
            
            st.markdown(f"<h2 style='text-align:center;'>{name}</h2>", unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{temp}°C")
            m2.metric(T["clouds"], f"{curr['clouds']['all']}%")
            m3.metric(T["wind"], f"{curr['wind']['speed']} m/s")
            m4.metric(T["humidity"], f"{curr['main']['humidity']}%")

            if analyze:
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12)

            # Footer Amazon
            p_cat = "umbrella" if "rain" in cond else "winter+jacket" if temp < 15 else "sunglasses"
            st.markdown(f"<p style='text-align:center; opacity:0.3; margin-top:50px;'>Created by: Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
            st.markdown(f"""<div class="amazon-footer">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="70"><br>
                <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold;">{T['shop']}</a>
            </div>""", unsafe_allow_html=True)
    else: st.error("Location not found.")
else:
    apply_elden_style("clear", 25)
