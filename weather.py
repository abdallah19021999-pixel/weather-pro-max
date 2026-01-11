import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

# استدعاء الأسرار
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# 2. دالة إرسال إشعار لتيليجرام
def notify_me(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except: pass

# 3. جلب بيانات الطقس
@st.cache_data(ttl=600)
def get_weather_data(city_name):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(city_name)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={translated}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            notify_me(f"🔔 بحث جديد عن: {city_name}\n🌡️ {data['main']['temp']}°C")
            return data
        return None
    except: return None

def load_lottieurl(url: str):
    try: return requests.get(url).json()
    except: return None

# --- تطبيق الـ CSS (شريط الإعلانات + التنسيق) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .stApp { background: linear-gradient(to bottom, #1e3c72, #2a5298); color: white; }
    
    /* شريط الإعلانات المتحرك */
    .ticker-wrapper {
        width: 100%; overflow: hidden; background: rgba(0,0,0,0.3);
        padding: 10px 0; border-bottom: 2px solid #007bff; margin-bottom: 20px;
    }
    .ticker-text {
        display: inline-block; white-space: nowrap;
        animation: ticker 20s linear infinite; font-weight: bold; font-size: 1.1rem;
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    
    /* تنسيق صندوق البحث */
    div[data-testid="stVerticalBlock"] > div:has(input) {
        max-width: 450px; margin: 0 auto !important;
        background: white !important; padding: 5px !important; border-radius: 25px !important;
    }
    input { color: black !important; text-align: center !important; font-size: 1.2rem !important; }
    
    /* تنسيق الزرار */
    div.stButton > button {
        background: #007bff; color: white; border-radius: 20px; 
        width: 250px; margin: 20px auto; display: block; height: 3.5em; font-weight: bold;
    }
    </style>
    
    <div class="ticker-wrapper">
        <div class="ticker-text">
            🚀 Weather Pro Max 2026: استمتع بأدق بيانات الطقس عالمياً | تم التطوير بواسطة عبد الله نبيل | تابع آخر التحديثات عبر البوت الخاص بنا 🌤️
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌤️ Weather Pro Max</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    city = st.text_input("", value="Alexandria")

weather_data = get_weather_data(city)

if weather_data:
    # الأنميشن
    main_cond = weather_data['weather'][0]['main'].lower()
    lottie_json = load_lottieurl("https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json")
    if lottie_json: st_lottie(lottie_json, height=220)

    if st.button("Get Detailed Report"):
        st.markdown("---")
        # إضافة فرصة الأمطار (OpenWeather يوفرها أحياناً في خانة 'rain' أو 'clouds')
        rain_chance = weather_data.get('rain', {}).get('1h', 0) 
        clouds = weather_data['clouds']['all']
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temp", f"{weather_data['main']['temp']} °C")
        col2.metric("Wind", f"{weather_data['wind']['speed']} m/s")
        col3.metric("Humidity", f"{weather_data['main']['humidity']}%")
        col4.metric("Rain/Clouds", f"{rain_chance if rain_chance > 0 else clouds}%")
        
        st.markdown("---")
        l, r = st.columns([2, 1])
        with l:
            st.map(pd.DataFrame({'lat': [weather_data['coord']['lat']], 'lon': [weather_data['coord']['lon']]}))
        with r:
            icon = weather_data['weather'][0]['icon']
            st.image(f"http://openweathermap.org/img/wn/{icon}@4x.png", caption=weather_data['weather'][0]['description'])

st.markdown("<br><center>Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
