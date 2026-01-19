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

# --- القاموس ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Type City Name...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind", "humidity": "Humidity",
        "hourly": "Next Hours Forecast", "shop": "Shop Deals on Amazon 🛒"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "اكتب اسم المدينة...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "hourly": "توقعات الساعات القادمة", "shop": "تسوق عروض أمازون 🛒"
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
        curr_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        fore_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        return requests.get(curr_url).json(), requests.get(fore_url).json()
    except: return None, None

# --- واجهة الـ CSS الأصلية ---
def apply_ui_final(cond, temp):
    cond = cond.lower()
    p_color = "#4facfe" if "rain" in cond else "#ffeb3b" if "clear" in cond else "#94a3b8"
    p_speed = "1s" if "rain" in cond else "10s" if "clear" in cond else "6s"
    particles = "".join([f'<div class="particle" style="left:{random.randint(0, 95)}%; animation-delay:-{random.uniform(0, 10)}s;"></div>' for i in range(20)])
    
    st.markdown(f"""
        <style>
        #MainMenu, footer, header, .stAppDeployButton, #viewerBadge {{visibility: hidden !important; display: none !important;}}
        .stApp {{ background: transparent !important; }}
        .bg {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: radial-gradient(circle at center, #111 0%, #000 100%); z-index: -1; overflow: hidden; }}
        .particle {{ position: absolute; background: {p_color}; width: 1.5px; height: 15px; opacity: 0.3; will-change: transform; animation: fall {p_speed} linear infinite; }}
        @keyframes fall {{ from {{ transform: translateY(-20vh); }} to {{ transform: translateY(110vh); }} }}
        .block-container {{padding-top: 2rem;}}
        [data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(8px); border-radius: 12px !important; padding: 10px !important; border: 1px solid rgba(255,255,255,0.1); }}
        .stButton button {{ background: {p_color} !important; color: black !important; font-weight: bold !important; width: 100% !important; border-radius: 10px !important; }}
        h1, h2, h3 {{ text-align: center !important; color: white !important; }}
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
            
            # --- نظام التحذيرات الشامل (All Weather Alerts) ---
            cond = curr_data['weather'][0]['main'].lower()
            temp = curr_data['main']['temp']
            wind = curr_data['wind']['speed']
            vis = curr_data.get('visibility', 10000)
            hum = curr_data['main']['humidity']
            
            alerts = []
            # 1. أمطار وعواصف رعدية
            if "rain" in cond: alerts.append("⚠️ مطر متوقع! خذ مظلتك" if st.session_state.lang=="AR" else "⚠️ Rain expected! Take an umbrella")
            if "thunderstorm" in cond: alerts.append("⚡ عاصفة رعدية! ابقَ في الداخل" if st.session_state.lang=="AR" else "⚡ Thunderstorm! Stay indoors")
            # 2. ثلوج
            if "snow" in cond: alerts.append("❄️ تساقط ثلوج! الجو شديد البرودة" if st.session_state.lang=="AR" else "❄️ Snowing! It's freezing")
            # 3. حرارة وبرودة شديدة
            if temp > 38: alerts.append("🔥 حرارة شديدة! اشرب ماءً" if st.session_state.lang=="AR" else "🔥 Extreme Heat! Drink water")
            if temp < 5: alerts.append("🥶 برد قارص! ارتِدِ ملابس ثقيلة" if st.session_state.lang=="AR" else "🥶 Very Cold! Wear heavy clothes")
            # 4. رياح وأعاصير
            if wind > 12: alerts.append("💨 رياح قوية! انتبه أثناء القيادة" if st.session_state.lang=="AR" else "💨 High Wind! Drive carefully")
            if "tornado" in cond or "squall" in cond: alerts.append("🌪️ تحذير من إعصار أو عاصفة شديدة!" if st.session_state.lang=="AR" else "🌪️ Tornado / Squall Warning!")
            # 5. شبورة ورؤية
            if vis < 2000: alerts.append("🌫️ شبورة كثيفة! الرؤية ضعيفة" if st.session_state.lang=="AR" else "🌫️ Thick Fog! Low visibility")
            # 6. رطوبة
            if hum > 90: alerts.append("💦 رطوبة عالية جداً تخنق" if st.session_state.lang=="AR" else "💦 Very High Humidity")

            for alert in alerts:
                st.warning(alert)

            st.markdown(f"<h2>{name}</h2>", unsafe_allow_html=True)
            
            # البيانات الحالية
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{temp}°C")
            m2.metric(T["clouds"], f"{curr_data['clouds']['all']}%")
            m3.metric(T["wind"], f"{wind} m/s")
            m4.metric(T["humidity"], f"{hum}%")
            
            # توقعات الساعات
            st.markdown(f"<h3>{T['hourly']}</h3>", unsafe_allow_html=True)
            f_cols = st.columns(5)
            for i, item in enumerate(fore_data['list'][:5]):
                with f_cols[i]:
                    time = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                    st.markdown(f'<div class="forecast-box"><small style="color:#ccc">{time}</small><br><b style="color:white">{item["main"]["temp"]}°C</b><br><small style="color:#aaa">{item["weather"][0]["main"]}</small></div>', unsafe_allow_html=True)

            if analyze_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=10)
            
            st.markdown(f'<div style="background:#ff9900; padding:12px; border-radius:12px; text-align:center; margin-top:20px;"><a href="https://www.amazon.eg/s?k=weather&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:black; font-weight:bold;">{T["shop"]}</a></div>', unsafe_allow_html=True)
    else:
        st.error("City not found!")
else:
    apply_ui_final("clear", 25)

st.markdown(f"<p style='text-align:center; opacity:0.3; margin-top:50px; color:white;'>Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
