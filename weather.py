import streamlit as st
import requests
import pandas as pd
import random
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Weather Pro Max", 
    page_icon="🌤️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. جلب المفاتيح من الـ Secrets
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except:
    st.error("Missing Secrets Configuration!")
    st.stop()

AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "AR"

# --- دالة إرسال تنبيه للتليجرام ---
def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, json=payload)
    except: pass

# --- القاموس (تم إضافة Hourly) ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Type City Name...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind", "humidity": "Humidity",
        "hourly": "Next Hours Forecast",
        "shop": "Shop Deals on Amazon 🛒"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "اكتب اسم المدينة...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "hourly": "توقعات الساعات القادمة",
        "shop": "تسوق عروض أمازون 🛒"
    }
}
T = texts[st.session_state.lang]

# --- دوال البحث والطقس ---
@st.cache_data(ttl=600)
def search_city(query):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=1&appid={API_KEY}"
        res = requests.get(geo_url).json()
        return (res[0]['lat'], res[0]['lon'], res[0]['name']) if res else (None, None, None)
    except: return None, None, None

@st.cache_data(ttl=600)
def get_weather_full(lat, lon):
    try:
        # الحالي
        curr_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        # التوقعات
        fore_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        curr = requests.get(curr_url).json()
        fore = requests.get(fore_url).json()
        return curr, fore
    except: return None, None

# --- الواجهة السلسة (نفس الـ CSS بتاعك بدون تغيير) ---
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
        .forecast-box {{ background: rgba(255,255,255,0.03); border-radius: 10px; padding: 10px; text-align: center; border: 1px solid rgba(255,255,255,0.05); }}
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
        send_telegram_alert(f"📍 New Search: {name} ({query})")
        curr_data, fore_data = get_weather_full(lat, lon)
        
        if curr_data:
            apply_ui_final(curr_data['weather'][0]['main'], curr_data['main']['temp'])
            
          # --- نسخة مطورة من دالة التحذير (Advanced Alerts) ---
def get_advanced_alerts(data, lang):
    temp = data['main']['temp']
    wind = data['wind']['speed']
    vis = data.get('visibility', 10000) # الرؤية بالأمتار
    hum = data['main']['humidity']
    condition = data['weather'][0]['main'].lower()
    
    alerts = []
    
    if "rain" in condition:
        alerts.append("⚠️ ستمطر قريباً! خذ مظلتك" if lang == "AR" else "⚠️ Rain expected! Take an umbrella")
    
    if temp > 38:
        alerts.append("🔥 حرارة شديدة! اشرب ماءً" if lang == "AR" else "🔥 Extreme Heat! Drink water")
    
    if wind > 12:
        alerts.append("💨 رياح قوية! انتبه أثناء القيادة" if lang == "AR" else "💨 High Wind! Be careful driving")
        
    if vis < 2000: # أقل من 2 كم
        alerts.append("🌫️ شبورة كثيفة! الرؤية ضعيفة" if lang == "AR" else "🌫️ Thick Fog! Low visibility")
        
    if hum > 90:
        alerts.append("💦 رطوبة عالية جداً تخنق!" if lang == "AR" else "💦 Very High Humidity!")
        
    return alerts
            st.markdown(f"<h2>{name}</h2>", unsafe_allow_html=True)
            
            # --- 2. البيانات الحالية ---
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{curr_data['main']['temp']}°C")
            m2.metric(T["clouds"], f"{curr_data['clouds']['all']}%")
            m3.metric(T["wind"], f"{curr_data['wind']['speed']} m/s")
            m4.metric(T["humidity"], f"{curr_data['main']['humidity']}%")
            
            # --- 3. توقعات الساعات القادمة (الإضافة الجديدة) ---
            st.markdown(f"<h3 style='color:white; text-align:center; margin-top:20px;'>{T['hourly']}</h3>", unsafe_allow_html=True)
            f_cols = st.columns(5)
            for i, item in enumerate(fore_data['list'][:5]):
                with f_cols[i]:
                    time = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                    st.markdown(f"""
                    <div class="forecast-box">
                        <small style='color:#ccc'>{time}</small><br>
                        <b style='font-size:1.1rem; color:white'>{item['main']['temp']}°C</b><br>
                        <small style='color:#aaa'>{item['weather'][0]['main']}</small>
                    </div>
                    """, unsafe_allow_html=True)

            if analyze_btn:
                st.markdown("<br>", unsafe_allow_html=True)
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

