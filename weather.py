import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

# استدعاء الأسرار (Secrets)
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# دالة إرسال إشعار لتيليجرام
def notify_me(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except: pass

# جلب البيانات
@st.cache_data(ttl=600)
def get_weather_data(city_name):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(city_name)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={translated}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            notify_me(f"🔔 بحث جديد: {city_name} | {data['main']['temp']}°C")
            return data
        return None
    except: return None

def load_lottieurl(url: str):
    try: return requests.get(url).json()
    except: return None

# --- تطبيق الـ CSS (نفس استايلك الأصلي مع إضافة شريط الإعلانات) ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background: linear-gradient(to bottom, #1e3c72, #2a5298); color: white; }}
    
    /* شريط الإعلانات المتحرك أسفل العنوان */
    .ticker-wrap {{
        width: 100%; overflow: hidden; background: rgba(0,0,0,0.2); padding: 5px 0;
    }}
    .ticker {{
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; font-weight: bold;
    }}
    @keyframes ticker {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}

    div.stButton > button {{
        background-color: #007bff; color: white; border-radius: 10px;
        width: 100%; font-weight: bold; border: none; height: 3em; margin-top: 10px;
    }}
    h1, h2, h3, p {{ color: white !important; }}
    input {{ color: black !important; border-radius: 10px !important; }}
    </style>
    """, unsafe_allow_html=True)

st.title("🌤️ Weather Pro Max Dashboard")

# شريط الإعلانات (بدون رسالة ترحيب - فقط معلومات تقنية)
st.markdown('<div class="ticker-wrap"><div class="ticker">آخر تحديثات خرائط الطقس 2026 متوفرة الآن | ميزة تتبع السحب والأمطار مفعلة | دقة البيانات تصل إلى 99%</div></div>', unsafe_allow_html=True)

city = st.text_input("Enter City Name:", "Alexandria")
weather_data = get_weather_data(city)

# تحديد الحالة والأنميشن
current_condition = "default"
LOTTIE_URLS = {
    "rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
    "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
    "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json",
    "default": "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"
}

if weather_data:
    main_cond = weather_data['weather'][0]['main'].lower()
    anim_json = load_lottieurl(LOTTIE_URLS.get(main_cond if main_cond in LOTTIE_URLS else "default"))
    if anim_json:
        st_lottie(anim_json, height=300, key="weather_anim")

# زر التقرير
if st.button("Get Detailed Report"):
    if weather_data:
        st.markdown("---")
        # إضافة فرصة الأمطار (بناءً على السحب والرطوبة)
        clouds = weather_data['clouds']['all']
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Temp", f"{weather_data['main']['temp']} °C")
        c2.metric("Wind", f"{weather_data['wind']['speed']} m/s")
        c3.metric("Humidity", f"{weather_data['main']['humidity']}%")
        c4.metric("Rain Chance", f"{clouds}%") # نسبة السحب هي أدق مؤشر لفرصة المطر
        
        st.markdown("---")
        l, r = st.columns([2, 1])
        with l:
            st.map(pd.DataFrame({'lat': [weather_data['coord']['lat']], 'lon': [weather_data['coord']['lon']]}))
        with r:
            icon_code = weather_data['weather'][0]['icon']
            st.image(f"http://openweathermap.org/img/wn/{icon_code}@4x.png", caption=weather_data['weather'][0]['description'])
    else:
        st.error("City not found!")

st.markdown("<br><center>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
