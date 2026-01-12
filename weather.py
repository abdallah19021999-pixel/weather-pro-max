import streamlit as st
import requests
import pandas as pd
from deep_translator import GoogleTranslator
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- القاموس اللغوي ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Search city, village, or district...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind Speed", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒", "alert_title": "⚠️ Safety Alert:"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "ابحث عن مدينة، قرية، أو حي...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق عروض أمازون 🛒", "alert_title": "⚠️ تنبيه للسلامة:"
    }
}
T = texts[st.session_state.lang]

# --- محركات البحث (تم دمج المحركين لضمان عدم حدوث Location not found) ---
@st.cache_data(ttl=3600)
def get_global_coords(city_query):
    try:
        # المحرك الأول: Nominatim للبحث العالمي الدقيق
        url = f"https://nominatim.openstreetmap.org/search?q={city_query}&format=json&limit=1"
        res = requests.get(url, headers={'User-Agent': 'WeatherPro_Final_Version'}).json()
        if res: 
            return float(res[0]['lat']), float(res[0]['lon']), res[0]['display_name']
        
        # المحرك الثاني الاحتياطي: Direct API لو الأول فشل
        url_alt = f"https://api.openweathermap.org/geo/1.0/direct?q={city_query}&limit=1&appid={API_KEY}"
        res_alt = requests.get(url_alt).json()
        if res_alt:
            return res_alt[0]['lat'], res_alt[0]['lon'], res_alt[0]['name']
            
        return None, None, None
    except: return None, None, None

@st.cache_data(ttl=600)
def get_weather_data(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        return requests.get(url).json()
    except: return None

# --- نظام التنبيهات الجوية ---
def show_alerts(data):
    w_speed = data['wind']['speed']
    temp = data['main']['temp']
    main_cond = data['weather'][0]['main'].lower()
    alert_msg = ""
    
    if w_speed > 10:
        alert_msg = "رياح قوية وأتربة! يرجى ارتداء الكمامة وحماية العين." if st.session_state.lang == "AR" else "High winds & dust! Please wear a mask and protect your eyes."
    elif "rain" in main_cond or "thunderstorm" in main_cond:
        alert_msg = "تنبيه أمطار! تجنب المناطق المنخفضة وأعمدة الكهرباء." if st.session_state.lang == "AR" else "Rain alert! Avoid low-lying areas and electric poles."
    elif temp > 38:
        alert_msg = "موجة حر! تجنب الشمس المباشرة واشرب السوائل." if st.session_state.lang == "AR" else "Heatwave! Avoid direct sun and drink plenty of water."

    if alert_msg:
        st.markdown(f"""<div style="background: rgba(255, 75, 75, 0.25); border: 2px solid #ff4b4b; padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 25px; backdrop-filter: blur(10px);">
            <p style="color: #ff4b4b; font-weight: bold; margin:0; font-size: 1.1rem;">{T['alert_title']} {alert_msg}</p>
        </div>""", unsafe_allow_html=True)

# --- محرك الجرافيكس الدائم ---
def apply_visuals(condition, temp):
    condition = condition.lower()
    if "rain" in condition: p_color, p_w, p_h, p_speed, p_count = "#4facfe", "2px", "30px", "0.8s", 60
    elif "snow" in condition or temp <= 2: p_color, p_w, p_h, p_speed, p_count = "#ffffff", "10px", "10px", "5s", 50
    elif "clear" in condition: p_color, p_w, p_h, p_speed, p_count = "#ffeb3b", "150px", "150px", "12s", 6
    else: p_color, p_w, p_h, p_speed, p_count = "#94a3b8", "3px", "3px", "7s", 30

    particles = "".join([f'<div class="particle" style="left:{random.randint(0, 100)}%; animation-delay:-{random.uniform(0, 10)}s;"></div>' for i in range(p_count)])
    st.markdown(f"""<style>
        .stApp {{ background: transparent !important; }}
        .bg {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: radial-gradient(circle at center, #1a1a1c 0%, #000 100%); z-index: -1; overflow: hidden; }}
        .particle {{ position: absolute; background: {p_color}; width: {p_w}; height: {p_h}; opacity: 0.4; border-radius: {"50%" if "rain" not in condition else "0%"}; filter: {"blur(50px)" if "clear" in condition else "none"}; animation: fall {p_speed} linear infinite; }}
        @keyframes fall {{ 0% {{ transform: translateY(-20vh); }} 100% {{ transform: translateY(110vh); }} }}
        .stTextInput {{ max-width: 450px !important; margin: 0 auto !important; }}
        .stTextInput input {{ background: white !important; color: #111 !important; border-radius: 12px !important; text-align: center; border: 3px solid {p_color}; font-weight: bold; }}
        [data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(15px); border-radius: 20px !important; padding: 20px !important; display: flex !important; flex-direction: column !important; align-items: center !important; }}
        [data-testid="stMetricValue"] {{ color: {p_color if "clear" not in condition else "#ffeb3b"} !important; font-size: 2.2rem !important; text-align: center !important; }}
        .stButton {{ display: flex; justify-content: center; }}
        .stButton button {{ background: {p_color if "clear" not in condition else "#ff9900"} !important; color: #000 !important; font-weight: bold !important; border-radius: 10px !important; }}
        .amazon-card {{ background: white; color: #232f3e; padding: 20px; border-radius: 20px; text-align: center; margin: 40px auto; max-width: 450px; border-bottom: 5px solid #ff9900; }}
        h1, h2 {{ text-align: center !important; color: white !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        </style><div class="bg">{particles}</div>""", unsafe_allow_html=True)

# --- واجهة المستخدم ---
st.markdown(f"<h1>{T['title']}</h1>", unsafe_allow_html=True)

# زرار اللغة
c1, c2, c3 = st.columns([4.5, 1, 4.5])
with c2:
    if st.button("🌐 AR/EN", use_container_width=True):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"; st.rerun()

# البحث
query = st.text_input("📍", placeholder=T["search_place"], label_visibility="collapsed")

# زرار الخريطة والتحليل
bc1, bc2, bc3 = st.columns([1, 1.2, 1])
with bc2: analyze_click = st.button(T["btn_analyze"], use_container_width=True)

if query:
    lat, lon, full_name = get_global_coords(query)
    if lat:
        data = get_weather_data(lat, lon)
        if data:
            apply_visuals(data['weather'][0]['main'], data['main']['temp'])
            st.markdown(f"<h2>{query.title()}</h2>", unsafe_allow_html=True)
            
            show_alerts(data) # نظام التنبيهات
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{data['main']['temp']}°C")
            m2.metric(T["clouds"], f"{data['clouds']['all']}%")
            m3.metric(T["wind"], f"{data['wind']['speed']} m/s")
            m4.metric(T["humidity"], f"{data['main']['humidity']}%")
            
            if analyze_click:
                st.markdown("<br>", unsafe_allow_html=True)
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12)

            st.markdown(f"""<div class="amazon-card">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="80"><br>
                <a href="https://www.amazon.eg/s?k=weather&tag={AFFILIATE_ID}" target="_blank" style="color:#0066c0; font-weight:bold; text-decoration:none;">{T['shop']}</a>
            </div>""", unsafe_allow_html=True)
    else:
        st.error("Location not found. Please try again.")
else:
    apply_visuals("clear", 25)

st.markdown(f"<p style='text-align:center; opacity:0.3; margin-top:50px;'>Created by: Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
