import streamlit as st
import requests
import pandas as pd
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

# التأكد من المفتاح
if "OPENWEATHER_API_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- القاموس ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Type City Name (e.g. Cairo)...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind Speed", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒", "alert": "⚠️ Safety Alert:"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "اكتب اسم المدينة (مثلاً: القاهرة)...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق عروض أمازون 🛒", "alert": "⚠️ تنبيه للسلامة:"
    }
}
T = texts[st.session_state.lang]

# --- محرك البحث الاحترافي (Direct OpenWeather Geocoding) ---
@st.cache_data(ttl=3600)
def search_city(query):
    try:
        # الطريقة دي هي الأضمن للموبايل ولأي مكان في العالم
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=1&appid={API_KEY}"
        res = requests.get(geo_url).json()
        if res:
            return res[0]['lat'], res[0]['lon'], res[0]['name']
        
        # محرك احتياطي لو البحث المباشر لم ينجح
        url_alt = f"https://api.openweathermap.org/data/2.5/weather?q={query}&appid={API_KEY}"
        res_alt = requests.get(url_alt).json()
        if res_alt.get("cod") == 200:
            return res_alt['coord']['lat'], res_alt['coord']['lon'], res_alt['name']
            
        return None, None, None
    except:
        return None, None, None

@st.cache_data(ttl=600)
def get_weather(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        return requests.get(url).json()
    except: return None

# --- الجرافيكس والتنبيهات ---
def apply_ui(cond, temp, data):
    cond = cond.lower()
    if "rain" in cond: p_color, p_speed = "#4facfe", "0.8s"
    elif "snow" in cond or temp <= 2: p_color, p_speed = "#ffffff", "5s"
    elif "clear" in cond: p_color, p_speed = "#ffeb3b", "12s"
    else: p_color, p_speed = "#94a3b8", "7s"

    particles = "".join([f'<div class="particle" style="left:{random.randint(0, 100)}%; animation-delay:-{random.uniform(0, 10)}s;"></div>' for i in range(50)])
    
    # رسالة التنبيه
    alert_html = ""
    if data['wind']['speed'] > 10 or "rain" in cond or temp > 38:
        msg = "انتبه من تقلبات الجو!" if st.session_state.lang == "AR" else "Watch out for weather changes!"
        alert_html = f'<div style="background:rgba(255,75,75,0.2); border:2px solid #ff4b4b; padding:10px; border-radius:10px; text-align:center; margin-bottom:20px; color:white;">{T["alert"]} {msg}</div>'

    st.markdown(f"""
        <style>
        .stApp {{ background: transparent !important; }}
        .bg {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: radial-gradient(circle at center, #1a1a1c 0%, #000 100%); z-index: -1; overflow: hidden; }}
        .particle {{ position: absolute; background: {p_color}; width: 2px; height: 20px; opacity: 0.4; animation: fall {p_speed} linear infinite; }}
        @keyframes fall {{ 0% {{ transform: translateY(-10vh); }} 100% {{ transform: translateY(110vh); }} }}
        .stTextInput {{ max-width: 450px !important; margin: 0 auto !important; }}
        .stTextInput input {{ border-radius: 12px !important; text-align: center; border: 2px solid {p_color} !important; }}
        [data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(10px); border-radius: 15px !important; padding: 15px !important; text-align: center !important; }}
        .stButton {{ display: flex; justify-content: center; }}
        .stButton button {{ background: {p_color} !important; color: black !important; font-weight: bold !important; width: 450px !important; border-radius: 10px !important; }}
        h1, h2 {{ text-align: center !important; color: white !important; }}
        </style>
        <div class="bg">{particles}</div>
    """, unsafe_allow_html=True)
    return alert_html

# --- التنفيذ ---
st.markdown(f"<h1>{T['title']}</h1>", unsafe_allow_html=True)

# زر اللغة بـ Key فريد جداً
if st.button("🌐 AR/EN", key="unique_lang_btn"):
    st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
    st.rerun()

query = st.text_input("📍", placeholder=T["search_place"], key="unique_search_input", label_visibility="collapsed")

# زر التحليل بـ Key فريد جداً
analyze_btn = st.button(T["btn_analyze"], key="unique_analyze_btn")

if query:
    lat, lon, name = search_city(query)
    if lat:
        data = get_weather(lat, lon)
        if data:
            alert_box = apply_ui(data['weather'][0]['main'], data['main']['temp'], data)
            st.markdown(f"<h2>{name}</h2>", unsafe_allow_html=True)
            st.markdown(alert_box, unsafe_allow_html=True)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{data['main']['temp']}°C")
            m2.metric(T["clouds"], f"{data['clouds']['all']}%")
            m3.metric(T["wind"], f"{data['wind']['speed']} m/s")
            m4.metric(T["humidity"], f"{data['main']['humidity']}%")
            
            if analyze_btn:
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=10)
            
            st.markdown(f'<div style="background:white; padding:10px; border-radius:15px; text-align:center; margin-top:20px;"><a href="https://www.amazon.eg/s?k=weather&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#111; font-weight:bold;">{T["shop"]}</a></div>', unsafe_allow_html=True)
    else:
        st.error("City not found. Please try another name.")
else:
    # خلفية افتراضية
    particles = "".join([f'<div class="particle" style="left:{random.randint(0, 100)}%; animation-delay:-{random.uniform(0, 10)}s;"></div>' for i in range(30)])
    st.markdown(f'<style>.stApp {{ background: transparent !important; }} .bg {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #000; z-index: -1; }} .particle {{ position: absolute; background: #555; width: 1px; height: 10px; animation: fall 10s linear infinite; }} @keyframes fall {{ 0% {{ translateY(-10vh); }} 100% {{ translateY(110vh); }} }} </style><div class="bg">{particles}</div>', unsafe_allow_html=True)

st.markdown(f"<p style='text-align:center; opacity:0.3; margin-top:50px;'>Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
