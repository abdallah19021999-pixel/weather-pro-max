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

# --- Translations Dictionary ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Search City or Village...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind Speed", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒", 
        "alert_rain": "⚠️ ALERT: Rain expected in the next 24 hours!",
        "no_rain": "🌤️ Clear skies expected.", "warn_search": "Please search for a location first!"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "ابحث عن قرية أو مدينة...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق على أمازون 🛒",
        "alert_rain": "⚠️ تنبيه: يتوقع سقوط أمطار خلال الـ 24 ساعة القادمة!",
        "no_rain": "🌤️ لا يوجد توقعات بأمطار اليوم.", "warn_search": "من فضلك ابحث عن مكان أولاً!"
    }
}
T = texts[st.session_state.lang]

# --- Core Functions ---
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

# --- الحماية والتنسيق البصري (Force Overlays) ---
def apply_visuals(condition, temp):
    bg = "linear-gradient(to bottom, #1e3c72, #2a5298)"
    overlay_html = ""
    
    # 🌧️ تأثير المطر (رسم يدوي SVG يظهر فوق كل شيء)
    if "rain" in condition or "drizzle" in condition:
        bg = "#1a1a1a"
        overlay_html = """
        <div style="position:fixed; top:0; left:0; width:100%; height:100%; z-index:999; pointer-events:none;">
            <svg width="100%" height="100%">
                <filter id="rain">
                    <feTurbulence type="fractalNoise" baseFrequency="0.01 0.5" numOctaves="1" result="noise"/>
                    <feDisplacementMap in="SourceGraphic" in2="noise" scale="20"/>
                </filter>
                <rect width="100%" height="100%" filter="url(#rain)" fill="transparent" opacity="0.3">
                    <animate attributeName="y" from="-100" to="100" dur="0.5s" repeatCount="indefinite" />
                </rect>
            </svg>
        </div>
        """
    # ☀️ تأثير التوهج الشمسي
    elif temp > 28 or "clear" in condition:
        bg = "linear-gradient(135deg, #FF8C00, #FFD700)"
        overlay_html = """
        <div style="position:fixed; top:0; left:0; width:100%; height:100%; z-index:999; pointer-events:none; 
             background: radial-gradient(circle at 80% 20%, rgba(255,255,255,0.4) 0%, transparent 50%);">
        </div>
        """

    st.markdown(f"""
        <style>
        .stApp {{ background: {bg} !important; transition: all 1s ease; color: white !important; }}
        /* تنسيق المقاييس في المنتصف بالضبط */
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(15px); border-radius: 20px; padding: 25px !important;
            border: 1px solid rgba(255,255,255,0.2); text-align: center !important;
            display: flex; flex-direction: column; align-items: center;
        }}
        [data-testid="stMetricValue"] {{ font-size: 2.2rem !important; width: 100%; text-align: center; display: block; }}
        [data-testid="stMetricLabel"] {{ font-size: 1.1rem !important; width: 100%; text-align: center; display: block; color: #eee !important; }}
        .alert-box {{
            padding: 15px; border-radius: 15px; background: rgba(255, 75, 75, 0.3);
            border: 2px solid #ff4b4b; text-align: center; margin-bottom: 20px; font-weight: bold; font-size: 1.2rem;
        }}
        .amazon-footer {{
            background: white; color: #232f3e; padding: 20px; border-radius: 20px;
            text-align: center; margin: 40px auto; border-bottom: 6px solid #ff9900;
            max-width: 500px; box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }}
        </style>
        {overlay_html}
        """, unsafe_allow_html=True)

# --- App Layout ---
h_c1, h_c2 = st.columns([9, 1])
with h_c1: st.title(T["title"])
with h_c2: 
    if st.button("🌐"):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

query = st.text_input("📍", placeholder=T["search_place"])
col_b1, col_b2, col_b3 = st.columns([1,1,1])
with col_b2: analyze_click = st.button(T["btn_analyze"], use_container_width=True)

if query:
    lat, lon, name = get_coordinates(query, st.session_state.lang)
    if lat:
        forecast = get_forecast(lat, lon)
        if forecast:
            curr = forecast['list'][0]
            cond, temp = curr['weather'][0]['main'].lower(), curr['main']['temp']
            apply_visuals(cond, temp)
            
            # Rain Alert Logic
            will_rain = any("rain" in f['weather'][0]['main'].lower() for f in forecast['list'][:8])
            if will_rain: st.markdown(f'<div class="alert-box">{T["alert_rain"]}</div>', unsafe_allow_html=True)
            
            st.markdown(f"<h2 style='text-align:center; text-shadow: 2px 2px 5px rgba(0,0,0,0.5);'>{name}</h2>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{temp}°C")
            m2.metric(T["clouds"], f"{curr['clouds']['all']}%")
            m3.metric(T["wind"], f"{curr['wind']['speed']} m/s")
            m4.metric(T["humidity"], f"{curr['main']['humidity']}%")

            if analyze_click:
                st.markdown("<div style='background:rgba(0,0,0,0.3); padding:20px; border-radius:20px; margin-top:20px; border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12)
                st.markdown("</div>", unsafe_allow_html=True)

            p_cat = "umbrella" if will_rain else "sunglasses" if temp > 28 else "winter+jacket"
            st.markdown(f"<p style='text-align:center; opacity:0.8; margin-top:50px;'>Created by: Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
            st.markdown(f"""<div class="amazon-footer">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="80"><br>
                <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold; font-size:1.1rem;">{T['shop']}</a>
            </div>""", unsafe_allow_html=True)
    else: st.error("Location not found.")
else:
    apply_visuals("clear", 25)
    if analyze_click: st.warning(T["warn_search"])
