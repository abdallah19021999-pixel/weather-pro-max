import streamlit as st
import requests
import pandas as pd
import random

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Weather Pro Max", 
    page_icon="🌤️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. جلب المفاتيح من الـ Secrets (API + Telegram)
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except:
    st.error("Missing Secrets Configuration!")
    st.stop()

AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- دالة إرسال تنبيه للتليجرام ---
def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, json=payload)
    except:
        pass

# --- القاموس ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Type City Name...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "اكتب اسم المدينة...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق عروض أمازون 🛒"
    }
}
T = texts[st.session_state.lang]

# --- دوال البحث والطقس ---
@st.cache_data(ttl=3600)
def search_city(query):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=1&appid={API_KEY}"
        res = requests.get(geo_url).json()
        return (res[0]['lat'], res[0]['lon'], res[0]['name']) if res else (None, None, None)
    except: return None, None, None

@st.cache_data(ttl=600)
def get_weather(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        return requests.get(url).json()
    except: return None

# --- الواجهة السلسة (Optimized UI) ---
def apply_ui_final(cond, temp):
    cond = cond.lower()
    if "rain" in cond: p_color, p_speed = "#4facfe", "1s"
    elif "clear" in cond: p_color, p_speed = "#ffeb3b", "10s"
    else: p_color, p_speed = "#94a3b8", "6s"

    particles = "".join([f'<div class="particle" style="left:{random.randint(0, 95)}%; animation-delay:-{random.uniform(0, 10)}s;"></div>' for i in range(20)])
    
    st.markdown(f"""
        <style>
        #MainMenu, footer, header, .stAppDeployButton, #viewerBadge, [data-testid="bundleHostBadge"] {{visibility: hidden !important; display: none !important;}}
        .stApp {{ background: transparent !important; }}
        .bg {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: radial-gradient(circle at center, #111 0%, #000 100%); z-index: -1; overflow: hidden; }}
        .particle {{ position: absolute; background: {p_color}; width: 1.5px; height: 15px; opacity: 0.3; will-change: transform; animation: fall {p_speed} linear infinite; }}
        @keyframes fall {{ from {{ transform: translateY(-20vh); }} to {{ transform: translateY(110vh); }} }}
        .block-container {{padding-top: 2rem;}}
        [data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(8px); border-radius: 12px !important; padding: 10px !important; border: 1px solid rgba(255,255,255,0.1); }}
        .stButton button {{ background: {p_color} !important; color: black !important; font-weight: bold !important; width: 100% !important; border-radius: 10px !important; }}
        h1, h2 {{ text-align: center !important; color: white !important; }}
        </style>
        <div class="bg">{particles}</div>
    """, unsafe_allow_html=True)

# --- التنفيذ الرئيسي ---
st.markdown(f"<h1>{T['title']}</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 0.6, 1])
with c2:
    if st.button("🌐 AR/EN"):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

query = st.text_input("", placeholder=T["search_place"], key="search_input", label_visibility="collapsed")
analyze_btn = st.button(T["btn_analyze"])

if query:
    lat, lon, name = search_city(query)
    if lat:
        # إرسال التنبيه فوراً
        send_telegram_alert(f"📍 New Search: {name} ({query})")
        
        data = get_weather(lat, lon)
        if data:
            apply_ui_final(data['weather'][0]['main'], data['main']['temp'])
            st.markdown(f"<h2>{name}</h2>", unsafe_allow_html=True)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{data['main']['temp']}°C")
            m2.metric(T["clouds"], f"{data['clouds']['all']}%")
            m3.metric(T["wind"], f"{data['wind']['speed']} m/s")
            m4.metric(T["humidity"], f"{data['main']['humidity']}%")
            
            if analyze_btn:
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=10)
            
            st.markdown(f'''
                <div style="background:#ff9900; padding:12px; border-radius:12px; text-align:center; margin-top:20px;">
                    <a href="https://www.amazon.eg/s?k=weather&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:black; font-weight:bold;">{T["shop"]}</a>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.error("City not found!")
else:
    apply_ui_final("clear", 25)

st.markdown(f"<p style='text-align:center; opacity:0.3; margin-top:50px; color:white;'>Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
