import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
AFFILIATE_ID = "abdallah2026-21"

# دالة "صياد الإحداثيات" - دي اللي هتجيب أي مكان في العالم
@st.cache_data(ttl=3600)
def get_coordinates(location_name):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(location_name)
        # بنبحث في سيرفر الجغرافيات عن الإحداثيات
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={translated}&limit=1&appid={API_KEY}"
        res = requests.get(geo_url, timeout=5).json()
        if res:
            return res[0]['lat'], res[0]['lon'], res[0]['name'] + ", " + res[0].get('country', '')
        return None, None, None
    except: return None, None, None

@st.cache_data(ttl=600)
def get_weather_by_coords(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        return requests.get(url, timeout=5).json()
    except: return None

def load_lottieurl(url: str):
    try: return requests.get(url).json()
    except: return None

# --- الـ CSS الأصلي ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background: linear-gradient(to bottom, #1e3c72, #2a5298); color: white; }}
    .ticker-wrap {{ width: 100%; overflow: hidden; background: rgba(0,0,0,0.3); padding: 8px 0; margin-bottom: 15px; }}
    .ticker {{ display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; font-weight: bold; color: #00d4ff; }}
    @keyframes ticker {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
    .amazon-ad-box {{ background: white; color: #232f3e; padding: 20px; border-radius: 15px; text-align: center; margin-top: 30px; border-bottom: 5px solid #ff9900; box-shadow: 0 10px 20px rgba(0,0,0,0.3); }}
    .ad-button {{ background-color: #ff9900; color: white !important; padding: 10px 25px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block; margin-top: 10px; }}
    [data-testid="stMetric"] {{ background: rgba(255,255,255,0.1); padding: 10px !important; border-radius: 10px; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="ticker-wrap"><div class="ticker">🌍 نظام البحث بالإحداثيات مفعل: الآن نصل لأصغر القرى والنجوع حول العالم بدقة الخرائط 🌤️</div></div>', unsafe_allow_html=True)

st.title("🌤️ Weather Pro Max Global AI")

city_query = st.text_input("📍 ابحث عن أي مكان (قرية، مركز، مدينة):", placeholder="اكتب اسم المكان هنا...")

if city_query:
    # الخطوة 1: نجيب الإحداثيات
    lat, lon, full_name = get_coordinates(city_query)
    
    if lat:
        # الخطوة 2: نجيب الطقس بناءً على الموقع الجغرافي
        weather_data = get_weather_by_coords(lat, lon)
        
        if weather_data:
            main_cond = weather_data['weather'][0]['main'].lower()
            temp = weather_data['main']['temp']

            # الروابط الذكية
            if "rain" in main_cond:
                ad_text, p_search = "☔ الدنيا بتمطر؟ الحق عروض الشماسي!", "umbrella"
            elif temp > 25:
                ad_text, p_search = "🕶️ الجو شمس؟ شوف نظارات الشمس الأصلية!", "sunglasses"
            elif temp < 15:
                ad_text, p_search = "🧥 الجو برد؟ شوف كولكشن الشتاء!", "winter+clothes"
            else:
                ad_text, p_search = "🎒 الجو رايق! شوف عروض الرحلات!", "backpacks"

            p_link = f"https://www.amazon.eg/s?k={p_search}&tag={AFFILIATE_ID}"

            # الأنميشن
            anim_urls = {"rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
                         "clear": "https://lottie.host/a8a5b293-61a7-47_b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
                         "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json",
                         "default": "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"}
            anim_json = load_lottieurl(anim_urls.get(main_cond, anim_urls["default"]))
            if anim_json: st_lottie(anim_json, height=220)

            st.subheader(f"📍 {full_name}")

            # المقاييس الـ 4
            c1, c2 = st.columns(2)
            c1.metric("Temperature", f"{temp} °C")
            c2.metric("Clouds", f"{weather_data['clouds']['all']}%")
            c3, c4 = st.columns(2)
            c3.metric("Wind Speed", f"{weather_data['wind']['speed']} m/s")
            c4.metric("Humidity", f"{weather_data['main']['humidity']}%")

            if st.button("Analysis & Map"):
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))

            st.markdown(f"""<div class="amazon-ad-box">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="90"><br>
                <p>{ad_text}</p>
                <a href="{p_link}" target="_blank" class="ad-button">اطلب الآن بخصم 🛒</a>
                </div>""", unsafe_allow_html=True)
    else:
        st.error("❌ لم نجد هذا المكان على الخريطة. حاول كتابة اسم القرية والمحافظة.")

st.markdown("<br><center style='opacity:0.7;'>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
