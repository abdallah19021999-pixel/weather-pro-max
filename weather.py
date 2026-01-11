import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide")

# استدعاء الأسرار (Secrets)
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# 2. الدوال الأساسية
def notify_me(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except: pass

@st.cache_data(ttl=600)
def get_weather_data(city_name):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(city_name)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={translated}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

def load_lottieurl(url: str):
    try: return requests.get(url).json()
    except: return None

# --- تصميم CSS احترافي (Modern Glassmorphism) ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{
        background: url("https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?ixlib=rb-1.2.1&auto=format&fit=crop&w=1920&q=80");
        background-size: cover;
    }}
    
    /* شريط الإعلانات العلوي */
    .ticker-container {{
        background: rgba(0, 0, 0, 0.6);
        color: #00d4ff;
        padding: 8px;
        font-weight: bold;
        text-align: center;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid rgba(255,255,255,0.1);
    }}

    /* تصميم البطاقات (Cards) */
    .metric-card {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        transition: 0.3s;
    }}
    .metric-card:hover {{
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.2);
    }}

    /* تحسين بوكس البحث */
    .stTextInput input {{
        background: rgba(255, 255, 255, 0.9) !important;
        color: #1e3c72 !important;
        border-radius: 30px !important;
        font-size: 1.2rem !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }}
    
    h1 {{ text-shadow: 2px 2px 10px rgba(0,0,0,0.5); }}
    </style>
    """, unsafe_allow_html=True)

# شريط الإعلانات
st.markdown('<div class="ticker-container">🚀 تحديثات 2026: تم تفعيل ميزة ذكاء خرائط الطقس وفرص الأمطار المباشرة</div>', unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white;'>🌤️ Weather Pro Max</h1>", unsafe_allow_html=True)

# منطقة البحث
c1, c2, c3 = st.columns([1, 1.5, 1])
with c2:
    city = st.text_input("", value="Alexandria", placeholder="Search city...")

weather_data = get_weather_data(city)

if weather_data:
    # إشعار تيليجرام
    notify_me(f"👤 مستخدم بحث عن: {city} | {weather_data['main']['temp']}°C")

    # عرض الأنميشن والبيانات الأساسية في صف واحد
    col_main1, col_main2 = st.columns([1, 1])
    with col_main1:
        lottie_json = load_lottieurl("https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json")
        if lottie_json: st_lottie(lottie_json, height=250)
    
    with col_main2:
        st.markdown(f"""
            <div style='text-align: center; margin-top: 50px;'>
                <h2 style='font-size: 4rem; color: white; margin: 0;'>{int(weather_data['main']['temp'])}°C</h2>
                <p style='font-size: 1.5rem; color: #ddd;'>{weather_data['weather'][0]['description'].capitalize()}</p>
            </div>
        """, unsafe_allow_html=True)

    # صف البطاقات الاحترافي
    st.markdown("### 📊 Live Statistics")
    m1, m2, m3, m4 = st.columns(4)
    
    # نسبة الأمطار (تعتمد على السحب والرطوبة كمعادلة تقريبية لو لم تتوفر مباشرة)
    rain_prob = weather_data.get('rain', {}).get('1h', weather_data['clouds']['all'] / 10)
    
    with m1:
        st.markdown(f'<div class="metric-card">💧<br><small>Humidity</small><br><h3>{weather_data["main"]["humidity"]}%</h3></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="metric-card">🌬️<br><small>Wind Speed</small><br><h3>{weather_data["wind"]["speed"]} m/s</h3></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="metric-card">🌧️<br><small>Rain Chance</small><br><h3>{int(rain_prob * 10)}%</h3></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card">🎈<br><small>Pressure</small><br><h3>{weather_data["main"]["pressure"]} hPa</h3></div>', unsafe_allow_html=True)

    # الخريطة في كارد كبير
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="metric-card">📍 <b>Live Location Tracking</b>', unsafe_allow_html=True)
        st.map(pd.DataFrame({'lat': [weather_data['coord']['lat']], 'lon': [weather_data['coord']['lon']]}))
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><center style='color: white; opacity: 0.6;'>Design & Dev by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
