import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide")

# --- استدعاء الأسرار من الخزنة (Secrets) ---
# دي الطريقة الصح عشان محدش يسرق التوكن بتاعك من GitHub
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# 2. دالة إرسال إشعار للبوت بتاعك (تيليجرام)
def notify_me(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
    except:
        pass

# 3. دالة جلب البيانات
@st.cache_data(ttl=600)
def get_weather_data(city_name):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(city_name)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={translated}&appid={API_KEY}&units=metric"
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            # هيبعتلك رسالة للبوت أول ما حد يبحث عن مدينة
            notify_me(f"🔔 مستخدم بحث عن: {city_name}\n🌡️ الحرارة: {data['main']['temp']}°C")
            return data
        return None
    except:
        return None

def load_lottieurl(url: str):
    try: return requests.get(url).json()
    except: return None

# --- التصميم ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background: linear-gradient(to bottom, #1e3c72, #2a5298); color: white; }}
    .stTextInput input {{ color: black !important; font-weight: bold; border-radius: 15px !important; text-align: center; }}
    div.stButton > button {{ background: #007bff; color: white; border-radius: 15px; width: 100%; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

st.title("🌤️ Weather Pro Max Dashboard")

# البحث (محدد العرض للموبايل والسنتر)
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    city = st.text_input("Enter City Name:", "Alexandria")

weather_data = get_weather_data(city)

# الأنميشن
LOTTIE_URLS = {
    "rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
    "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
    "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json",
    "default": "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"
}

if weather_data:
    main_cond = weather_data['weather'][0]['main'].lower()
    anim_url = LOTTIE_URLS.get(main_cond if main_cond in LOTTIE_URLS else "default")
    st_lottie(load_lottieurl(anim_url), height=250)

    if st.button("Get Detailed Report"):
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        col1.metric("Temp", f"{weather_data['main']['temp']} °C")
        col2.metric("Wind", f"{weather_data['wind']['speed']} m/s")
        col3.metric("Humidity", f"{weather_data['main']['humidity']}%")
        
        st.markdown("---")
        l, r = st.columns([2, 1])
        with l:
            st.map(pd.DataFrame({'lat': [weather_data['coord']['lat']], 'lon': [weather_data['coord']['lon']]}))
        with r:
            icon = weather_data['weather'][0]['icon']
            st.image(f"http://openweathermap.org/img/wn/{icon}@4x.png")
            st.write(f"Description: {weather_data['weather'][0]['description']}")

st.markdown("<br><center>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
