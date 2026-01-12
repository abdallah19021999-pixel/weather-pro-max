import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

# --- دالة جلب البيانات (محرك OSM الخارق) ---
@st.cache_data(ttl=3600)
def get_coordinates(location_name):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
        headers = {'User-Agent': 'WeatherApp_2026'}
        res = requests.get(url, headers=headers, timeout=10).json()
        if res: return float(res[0]['lat']), float(res[0]['lon']), res[0]['display_name']
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

# --- محرك التأثيرات البصرية (Dynamic Theme Engine) ---
def apply_weather_theme(condition, temp):
    # الحالة الافتراضية (صافي/مشمس)
    bg_color = "linear-gradient(135deg, #FF8C00 0%, #FFD700 100%)" # برتقالي وذهبي شمس
    text_shadow = "2px 2px 10px rgba(255, 215, 0, 0.5)"
    
    if "rain" in condition or "drizzle" in condition:
        bg_color = "linear-gradient(to bottom, #203a43, #2c5364)" # أزرق غامق ممطر
        text_shadow = "0px 0px 15px rgba(0, 191, 255, 0.6)"
    elif "cloud" in condition:
        bg_color = "linear-gradient(to right, #bdc3c7, #2c3e50)" # رمادي غيمي
        text_shadow = "none"
    elif temp < 15:
        bg_color = "linear-gradient(to top, #83a4d4, #b6fbff)" # ثلجي/بارد
        text_shadow = "0px 0px 10px white"

    st.markdown(f"""
        <style>
        .stApp {{
            background: {bg_color};
            background-attachment: fixed;
            transition: all 0.8s ease-in-out;
        }}
        .main-title {{
            font-size: 3rem !important;
            font-weight: 800;
            text-align: center;
            color: white;
            text-shadow: {text_shadow};
            margin-bottom: 20px;
        }}
        .amazon-ad-box {{
            background: rgba(255, 255, 255, 0.9);
            color: #232f3e;
            padding: 25px;
            border-radius: 20px;
            text-align: center;
            border-bottom: 8px solid #ff9900;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }}
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 15px !important;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        </style>
        """, unsafe_allow_html=True)

# واجهة المستخدم
st.markdown('<h1 class="main-title">🌤️ Weather Pro Max</h1>', unsafe_allow_html=True)

city_query = st.text_input("📍 ابحث عن أي مكان في العالم:", placeholder="اكتب اسم القرية أو المدينة هنا...")

if city_query:
    lat, lon, full_name = get_coordinates(city_query)
    
    if lat:
        weather_data = get_weather_by_coords(lat, lon)
        if weather_data:
            condition = weather_data['weather'][0]['main'].lower()
            temp = weather_data['main']['temp']
            
            # تطبيق الثيم الحي بناءً على حالة الجو
            apply_weather_theme(condition, temp)

            # الأنميشن
            anim_urls = {
                "rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
                "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
                "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json"
            }
            anim_json = load_lottieurl(anim_urls.get(condition, "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"))
            if anim_json: st_lottie(anim_json, height=250)

            st.markdown(f"<h3 style='text-align:center;'>📍 {full_name}</h3>", unsafe_allow_html=True)

            # المقاييس الأربعة بتصميم "الزجاج المضبب" (Glassmorphism)
            c1, c2 = st.columns(2)
            c1.metric("Temperature", f"{temp} °C")
            c2.metric("Clouds", f"{weather_data['clouds']['all']}%")
            c3, c4 = st.columns(2)
            c3.metric("Wind Speed", f"{weather_data['wind']['speed']} m/s")
            c4.metric("Humidity", f"{weather_data['main']['humidity']}%")

            # روابط أمازون الذكية
            p_search = "sunglasses" if temp > 25 else "winter+clothes" if temp < 15 else "umbrella" if "rain" in condition else "backpack"
            p_link = f"https://www.amazon.eg/s?k={p_search}&tag={AFFILIATE_ID}"

            st.markdown(f"""
                <div class="amazon-ad-box">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="100">
                    <p style="font-size:1.2rem; margin:15px 0;">اكتشف أفضل العروض المناسبة لجو {full_name} اليوم!</p>
                    <a href="{p_link}" target="_blank" style="background:#ff9900; color:white; padding:12px 30px; text-decoration:none; border-radius:30px; font-weight:bold;">تسوّق الآن 🛒</a>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Explore Detailed Map"):
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
    else:
        st.error("❌ لم نجد هذا المكان، جرب كتابته بدقة أكبر.")
else:
    # ثيم افتراضي هادئ قبل البحث
    st.markdown("<style>.stApp { background: linear-gradient(to bottom, #1e3c72, #2a5298); }</style>", unsafe_allow_html=True)

st.markdown("<br><center style='color:white; opacity:0.6;'>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
