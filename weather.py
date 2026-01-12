import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- قاموس اللغات المطور ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Search City or Village...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind Speed", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒", "alert_rain": "⚠️ ALERT: Rain expected in the next 24 hours! Take an umbrella.",
        "no_rain": "🌤️ No rain expected for the rest of the day."
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "ابحث عن قرية أو مدينة...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق على أمازون 🛒", "alert_rain": "⚠️ تنبيه: يتوقع سقوط أمطار خلال الـ 24 ساعة القادمة! خذ مظلتك.",
        "no_rain": "🌤️ لا يوجد توقعات بأمطار لبقية اليوم."
    }
}
T = texts[st.session_state.lang]

# --- جلب البيانات ---
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
def get_weather_forecast(lat, lon):
    try:
        # فحص التوقعات لـ 5 أيام (كل 3 ساعات)
        url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        return requests.get(url).json()
    except: return None

# --- تنسيقات CSS المتطورة (السنترة والتأثيرات) ---
def apply_visuals(condition, temp):
    bg, overlay = "linear-gradient(to bottom, #1e3c72, #2a5298)", ""
    if "rain" in condition or "drizzle" in condition:
        bg = "linear-gradient(to bottom, #203a43, #2c5364)"
        overlay = "url('https://www.transparenttextures.com/patterns/carbon-fibre.png')"
    elif temp > 28:
        bg = "linear-gradient(135deg, #FF8C00 0%, #FFD700 100%)"
        overlay = "radial-gradient(circle at top right, rgba(255,255,224,0.4), transparent)"

    st.markdown(f"""
        <style>
        .stApp {{ background: {bg}; background-image: {overlay if overlay else 'none'}; color: white !important; }}
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.15) !important;
            backdrop-filter: blur(10px); border-radius: 20px; padding: 20px !important;
            border: 1px solid rgba(255,255,255,0.2); text-align: center !important;
        }}
        [data-testid="stMetricValue"] {{ font-size: 2rem !important; justify-content: center !important; }}
        [data-testid="stMetricLabel"] {{ justify-content: center !important; color: #ddd !important; }}
        .alert-box {{
            padding: 15px; border-radius: 15px; background: rgba(255, 0, 0, 0.2);
            border: 1px solid red; text-align: center; margin-bottom: 20px; font-weight: bold;
        }}
        .amazon-footer {{
            background: white; color: #232f3e; padding: 20px; border-radius: 20px;
            text-align: center; margin: 40px auto; border-bottom: 6px solid #ff9900;
            max-width: 550px; box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        }}
        </style>
        """, unsafe_allow_html=True)

# --- واجهة المستخدم ---
c1, c2 = st.columns([9, 1])
with c1: st.title(T["title"])
with c2: 
    if st.button("🌐"):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

query = st.text_input("📍", placeholder=T["search_place"])
col1, col2, col3 = st.columns([1,1,1])
with col2: analyze = st.button(T["btn_analyze"], use_container_width=True)

if query:
    lat, lon, name = get_coordinates(query, st.session_state.lang)
    if lat:
        forecast_data = get_weather_forecast(lat, lon)
        if forecast_data:
            # الحالة الحالية
            current = forecast_data['list'][0]
            cond = current['weather'][0]['main'].lower()
            temp = current['main']['temp']
            apply_visuals(cond, temp)
            
            # --- نظام التنبؤ بالمطر (فحص أول 8 فترات = 24 ساعة) ---
            will_rain = any("rain" in f['weather'][0]['main'].lower() for f in forecast_data['list'][:8])
            
            if will_rain:
                st.markdown(f'<div class="alert-box">{T["alert_rain"]}</div>', unsafe_allow_html=True)
            else:
                st.info(T["no_rain"])

            st.markdown(f"<h2 style='text-align:center;'>{name}</h2>", unsafe_allow_html=True)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{temp}°C")
            m2.metric(T["clouds"], f"{current['clouds']['all']}%")
            m3.metric(T["wind"], f"{current['wind']['speed']} m/s")
            m4.metric(T["humidity"], f"{current['main']['humidity']}%")

            if analyze:
                st.markdown("<div style='background:rgba(0,0,0,0.2); padding:20px; border-radius:20px;'>", unsafe_allow_html=True)
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12)
                st.markdown("</div>", unsafe_allow_html=True)

            # Amazon Footer
            p_cat = "umbrella" if will_rain else "sunglasses" if temp > 28 else "winter+jacket"
            st.markdown(f"<p style='text-align:center; opacity:0.6; margin-top:50px;'>Created by: Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
            st.markdown(f"""
                <div class="amazon-footer">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="80"><br>
                    <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold;">{T['shop']}</a>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Location not found.")
else:
    apply_visuals("clear", 25)
