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

# دالة إرسال إشعار لتيليجرام
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

# --- تطبيق الـ CSS ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background: linear-gradient(to bottom, #1e3c72, #2a5298); color: white; }}
    
    .stTextInput > div > div > input {{
        border-radius: 15px !important;
        text-align: center !important;
    }}

    /* تصميم شريط إعلانات أمازون الذكي (ليظهر بالأسفل) */
    .amazon-ads {{
        background: white;
        color: #232f3e;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin: 25px 0;
        border-left: 5px solid #ff9900;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        font-family: sans-serif;
    }}
    .amazon-ads b {{ color: #ff9900; }}
    
    [data-testid="stMetric"] {{
        background: rgba(255,255,255,0.1);
        padding: 15px !important;
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("🌤️ Weather Pro Max Dashboard")

city = st.text_input("Enter City Name:", "Alexandria")
weather_data = get_weather_data(city)

if weather_data:
    main_cond = weather_data['weather'][0]['main'].lower()
    temp = weather_data['main']['temp']
    
    # تحضير محتوى الإعلان (سيتم عرضه بالأسفل)
    ad_content = ""
    if "rain" in main_cond:
        ad_content = "☔ الدنيا بتمطر؟ الحق عرض الشماسي والجاكيتات الووتر بروف على أمازون! <b>خصم 20%</b>"
    elif temp > 25:
        ad_content = "🕶️ الجو شمس؟ جرب نظارات Ray-Ban الأصلية، شياكة وحماية! <b>اطلبها الآن</b>"
    elif temp < 15:
        ad_content = "🧥 الجو برد؟ شوف كولكشن الشتاء الجديد والدفايات على أمازون! <b>بأفضل سعر</b>"
    else:
        ad_content = "🎒 طالع رحلة؟ شنط الظهر والرحلات المثالية مستنياك على أمازون!"

    # 1. عرض الأنميشن
    LOTTIE_URLS = {
        "rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
        "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
        "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json",
        "default": "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"
    }
    anim_json = load_lottieurl(LOTTIE_URLS.get(main_cond if main_cond in LOTTIE_URLS else "default"))
    if anim_json:
        st_lottie(anim_json, height=250, key="weather_anim")

    # 2. زر التقرير والبيانات المنظمة
    if st.button("Get Detailed Report"):
        notify_me(f"👤 بحث عن: {city} | {temp}°C")
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        c1.metric("Temperature", f"{temp} °C")
        c2.metric("Rain/Clouds", f"{weather_data['clouds']['all']}%")
        
        c3, c4 = st.columns(2)
        c3.metric("Wind Speed", f"{weather_data['wind']['speed']} m/s")
        c4.metric("Humidity", f"{weather_data['main']['humidity']}%")
        
        st.markdown("---")
        st.map(pd.DataFrame({'lat': [weather_data['coord']['lat']], 'lon': [weather_data['coord']['lon']]}))
        
        icon_code = weather_data['weather'][0]['icon']
        st.image(f"http://openweathermap.org/img/wn/{icon_code}@4x.png", width=100)

    # 3. عرض شريط إعلانات أمازون بالأسفل
    st.markdown(f'<div class="amazon-ads">🛒 <b>Amazon Offer:</b> {ad_content}</div>', unsafe_allow_html=True)

else:
    st.error("City not found!")

st.markdown("<br><center>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
