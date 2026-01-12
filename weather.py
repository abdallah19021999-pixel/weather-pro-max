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
        "title": "Weather Pro Max", "search_place": "Type city or village name...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind Speed", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒", 
        "alert_rain": "⚠️ Rain expected in the next 24 hours!",
        "warn_search": "Please enter a location first!"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "اكتب اسم المدينة أو القرية...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق على أمازون 🛒",
        "alert_rain": "⚠️ تنبيه: أمطار متوقعة خلال 24 ساعة!",
        "warn_search": "من فضلك ابحث عن مكان أولاً!"
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

# --- Custom UI CSS (Centering & Alignment Fix) ---
def apply_custom_style(condition, temp):
    accent = "#00f2ff" if "rain" in condition else "#ff9900"
    
    st.markdown(f"""
        <style>
        /* الخلفية العامة وتوسيط المحتوى */
        .stApp {{
            background: #0f172a !important;
            color: white !important;
            display: flex;
            align-items: center;
        }}
        
        /* ضبط صندوق البحث في المنتصف */
        .stTextInput {{
            max-width: 700px;
            margin: 0 auto;
        }}
        
        .stTextInput input {{
            background-color: white !important;
            color: #1e293b !important;
            border-radius: 12px !important;
            border: 3px solid {accent} !important;
            text-align: center; /* توسيط نص البحث */
        }}

        /* توسيط العناوين والأرقام داخل مربعات الـ Metrics */
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px);
            border-radius: 20px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            padding: 20px !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important; /* توسيط أفقي */
            justify-content: center !important; /* توسيط رأسي */
        }}
        
        [data-testid="stMetricValue"] {{ 
            color: {accent} !important; 
            font-size: 2.5rem !important;
            width: 100%;
            text-align: center !important;
            display: block !important;
        }}
        
        [data-testid="stMetricLabel"] {{ 
            color: #94a3b8 !important;
            width: 100%;
            text-align: center !important;
            display: block !important;
            font-size: 1.1rem !important;
            margin-bottom: 5px !important;
        }}

        /* الزرار الثابت موسط */
        .stButton {{
            display: flex;
            justify-content: center;
        }}
        
        .stButton button {{
            background: {accent} !important;
            color: #0f172a !important;
            font-weight: bold !important;
            border-radius: 12px !important;
            padding: 10px 40px !important;
            max-width: 400px;
        }}

        .alert-style {{
            background: rgba(255, 75, 75, 0.2);
            border: 1px solid #ff4b4b;
            padding: 15px;
            text-align: center;
            border-radius: 12px;
            max-width: 800px;
            margin: 0 auto 20px auto;
        }}

        .footer-amazon {{
            background: white;
            color: #232f3e;
            padding: 20px;
            border-radius: 20px;
            text-align: center;
            margin: 50px auto 0 auto;
            max-width: 600px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        h1, h2 {{
            text-align: center !important;
            width: 100%;
        }}
        </style>
    """, unsafe_allow_html=True)

# --- Layout ---
# هيدر موسط
st.markdown(f"<h1 style='color: white; margin-bottom: 0;'>{T['title']}</h1>", unsafe_allow_html=True)

# زرار اللغة في مكان منفصل تحت العنوان لضمان التنسيق
col_lang_1, col_lang_2, col_lang_3 = st.columns([4.5, 1, 4.5])
with col_lang_2:
    if st.button("🌐 AR/EN", use_container_width=True):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Search Box
query = st.text_input("📍", placeholder=T["search_place"], label_visibility="collapsed")

# Fixed Analyze Button
b_col1, b_col2, b_col3 = st.columns([1, 1.5, 1])
with b_col2:
    analyze_click = st.button(T["btn_analyze"], use_container_width=True)

if query:
    lat, lon, name = get_coordinates(query, st.session_state.lang)
    if lat:
        forecast = get_forecast(lat, lon)
        if forecast:
            curr = forecast['list'][0]
            cond, temp = curr['weather'][0]['main'].lower(), curr['main']['temp']
            apply_custom_style(cond, temp)
            
            # Rain Alert
            will_rain = any("rain" in f['weather'][0]['main'].lower() for f in forecast['list'][:8])
            if will_rain:
                st.markdown(f'<div class="alert-style">{T["alert_rain"]}</div>', unsafe_allow_html=True)
            
            st.markdown(f"<h2>{name}</h2>", unsafe_allow_html=True)
            
            # Metrics موسطة ومنظمة
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            with m_col1: st.metric(T["temp"], f"{temp}°C")
            with m_col2: st.metric(T["clouds"], f"{curr['clouds']['all']}%")
            with m_col3: st.metric(T["wind"], f"{curr['wind']['speed']} m/s")
            with m_col4: st.metric(T["humidity"], f"{curr['main']['humidity']}%")

            if analyze_click:
                st.markdown("<br>", unsafe_allow_html=True)
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12)

            # Footer
            p_cat = "umbrella" if will_rain else "sunglasses" if temp > 28 else "winter+jacket"
            st.markdown(f"<p style='text-align:center; opacity:0.5; margin-top:50px;'>Created by: Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
            st.markdown(f"""<div class="footer-amazon">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="80"><br>
                <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold; font-size:1.1rem;">{T['shop']}</a>
            </div>""", unsafe_allow_html=True)
    else:
        st.error("Location not found.")
else:
    apply_custom_style("clear", 25)
    if analyze_click:
        st.warning(T["warn_search"])
