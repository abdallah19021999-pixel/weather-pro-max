import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

# --- استدعاء الأسرار من الخزنة (Secrets) ---
# تأكد أنك أضفت هذه الأسماء في إعدادات Secrets بموقع Streamlit
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except Exception as e:
    st.error("خطأ: لم يتم العثور على مفاتيح السر (Secrets). يرجى ضبطها في إعدادات التطبيق.")
    st.stop()

# 2. دالة إرسال إشعار لتيليجرام
def notify_me(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except:
        pass

# 3. دالة جلب بيانات الطقس
@st.cache_data(ttl=600)
def get_weather_data(city_name):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(city_name)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={translated}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            notify_me(f"🔔 مستخدم بحث عن: {city_name}\n🌡️ الحرارة: {data['main']['temp']}°C")
            return data
        return None
    except:
        return None

# 4. دالة تحميل الأنميشن (مع معالجة الأخطاء)
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# روابط الأنميشن
LOTTIE_URLS = {
    "rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
    "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
    "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json",
    "default": "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"
}

# --- تطبيق الـ CSS ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background: linear-gradient(to bottom, #1e3c72, #2a5298); color: white; }}
    
    /* تنسيق صندوق البحث */
    div[data-testid="stVerticalBlock"] > div:has(input) {{
        width: 100%;
        max-width: 400px;
        margin: 0 auto !important;
        background: rgba(255, 255, 255, 0.95) !important;
        padding: 10px !important;
        border-radius: 15px !important;
    }}
    
    input {{ color: black !important; font-weight: bold !important; text-align: center !important; }}
    
    /* تنسيق الزرار */
    div.stButton > button {{
        background: #007bff; color: white; border-radius: 15px; 
        width: 100%; max-width: 250px; margin: 20px auto; display: block;
        font-weight: bold; border: none; height: 3.5em;
    }}
    
    h1, h2, h3, p {{ color: white !important; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

# --- واجهة المستخدم ---
st.markdown("<h1 style='text-align: center;'>🌤️ Weather Pro Max</h1>", unsafe_allow_html=True)

# وضع البحث في المنتصف
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    city = st.text_input("", value="Alexandria", placeholder="Enter City Name...")

weather_data = get_weather_data(city)

if weather_data:
    # معالجة الأنميشن بأمان
    main_cond = weather_data['weather'][0]['main'].lower()
    anim_url = LOTTIE_URLS.get(main_cond if main_cond in LOTTIE_URLS else "default")
    lottie_json = load_lottieurl(anim_url)
    
    if lottie_json:
        st_lottie(lottie_json, height=250, key="weather_anim")
    else:
        st.markdown("<h2 style='text-align: center;'>☁️</h2>", unsafe_allow_html=True)

    if st.button("Get Detailed Report"):
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("Temp", f"{weather_data['main']['temp']} °C")
        col2.metric("Wind", f"{weather_data['wind']['speed']} m/s")
        col3.metric("Humidity", f"{weather_data['main']['humidity']}%")
        
        st.markdown("---")
        # الخريطة والتفاصيل
        l, r = st.columns([2, 1])
        with l:
            st.map(pd.DataFrame({'lat': [weather_data['coord']['lat']], 'lon': [weather_data['coord']['lon']]}))
        with r:
            icon = weather_data['weather'][0]['icon']
            st.image(f"http://openweathermap.org/img/wn/{icon}@4x.png")
            st.write(f"Condition: {weather_data['weather'][0]['description'].capitalize()}")
else:
    st.warning("City not found. Please check the spelling.")

st.markdown("<br><center style='opacity: 0.7;'>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
