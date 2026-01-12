import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

# --- محركات البحث والبيانات ---
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

# --- محرك التأثيرات الجوية الحية (Rain/Snow/Sun Effects) ---
def apply_live_effects(condition, temp):
    effect_css = ""
    bg_gradient = "linear-gradient(to bottom, #1e3c72, #2a5298)" # Default
    
    if "rain" in condition or "drizzle" in condition:
        bg_gradient = "linear-gradient(to bottom, #203a43, #2c5364)"
        effect_css = """
        .stApp::before {
            content: ''; position: fixed; width: 100%; height: 100%; top: 0; left: 0;
            background-image: url('https://www.transparenttextures.com/patterns/carbon-fibre.png'), 
                              linear-gradient(to bottom, rgba(255,255,255,0.1) 10%, transparent 100%);
            animation: rain .3s linear infinite; z-index: 0; pointer-events: none;
        }
        @keyframes rain { 0% { background-position: 0 0; } 100% { background-position: 20px 100px; } }
        """
    elif "snow" in condition:
        bg_gradient = "linear-gradient(to bottom, #83a4d4, #b6fbff)"
        effect_css = """
        .stApp::before {
            content: '❄'; position: fixed; top: -10%; left: 50%; font-size: 24px; color: white;
            text-shadow: 0 0 5px #fff; animation: snow 5s linear infinite; z-index: 0; pointer-events: none;
        }
        @keyframes snow { 0% { transform: translateY(0) translateX(0); } 100% { transform: translateY(110vh) translateX(50px); } }
        """
    elif "clear" in condition or temp > 28:
        bg_gradient = "linear-gradient(135deg, #FF8C00 0%, #FFD700 100%)"
        effect_css = """
        .stApp::after {
            content: ''; position: fixed; top: -100px; right: -100px; width: 400px; height: 400px;
            background: radial-gradient(circle, rgba(255,255,224,0.4) 0%, transparent 70%);
            animation: shine 10s infinite alternate; pointer-events: none;
        }
        @keyframes shine { from { transform: scale(1); } to { transform: scale(1.3); } }
        """

    st.markdown(f"""
        <style>
        .stApp {{ background: {bg_gradient}; transition: background 1s ease; }}
        {effect_css}
        .main-card {{
            background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(15px);
            padding: 20px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.2);
            margin-bottom: 20px;
        }}
        .amazon-footer-ad {{
            background: white; color: #232f3e; padding: 15px; border-radius: 12px;
            text-align: center; margin-top: 50px; border-top: 4px solid #ff9900;
            max-width: 600px; margin-left: auto; margin-right: auto; font-size: 0.9rem;
        }}
        [data-testid="stMetric"] {{ background: rgba(0,0,0,0.2) !important; border-radius: 10px; }}
        </style>
        """, unsafe_allow_html=True)

# واجهة المستخدم
st.markdown('<h1 style="text-align:center; color:white; text-shadow: 2px 2px 10px rgba(0,0,0,0.5);">🌤️ Weather Pro Max</h1>', unsafe_allow_html=True)

city_query = st.text_input("📍 ابحث عن أي قرية أو مدينة:", placeholder="اكتب هنا...")

if city_query:
    lat, lon, full_name = get_coordinates(city_query)
    
    if lat:
        weather_data = get_weather_by_coords(lat, lon)
        if weather_data:
            cond = weather_data['weather'][0]['main'].lower()
            temp = weather_data['main']['temp']
            
            apply_live_effects(cond, temp)

            # عرض البيانات في كارت زجاجي
            with st.container():
                st.markdown(f"<div class='main-card'><h3 style='text-align:center;'>📍 {full_name}</h3>", unsafe_allow_html=True)
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("الحرارة", f"{temp} °C")
                c2.metric("الغيوم", f"{weather_data['clouds']['all']}%")
                c3.metric("الرياح", f"{weather_data['wind']['speed']} m/s")
                c4.metric("الرطوبة", f"{weather_data['main']['humidity']}%")
                
                # الخريطة رجعت
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=10)
                st.markdown("</div>", unsafe_allow_html=True)

            # ترشيحات ذكية للمنتجات
            if "rain" in cond:
                rec_text = "الدنيا بتمطر! ننصحك بـ: جاكيت وتربروف 🧥، شمسية متينة ☔، حذاء ضد الماء 🥾"
                p_search = "rain+gear+waterproof"
            elif temp > 28:
                rec_text = "الجو حر شمس! ننصحك بـ: نظارة شمسية 🕶️، واقي شمس 🧴، كاب قطني 🧢"
                p_search = "sunglasses+sunscreen+cap"
            elif temp < 15:
                rec_text = "الجو برد جداً! ننصحك بـ: بلوفر صوف 🧶، دفاية كهربائية ⚡، وشاح شتوي 🧣"
                p_search = "winter+clothes+heater"
            else:
                rec_text = "الجو رائع! ننصحك بـ: شنطة ظهر للرحلات 🎒، حذاء مريح 👟، زجاجة مياه رياضية 💧"
                p_search = "travel+backpack+shoes"

            p_link = f"https://www.amazon.eg/s?k={p_search}&tag={AFFILIATE_ID}"

            # الجزء السفلي (الاسم + الإعلان الصغير)
            st.markdown(f"""
                <center style='color:white; opacity:0.8; margin-top:40px;'>Created by: Abdallah Nabil | 2026</center>
                <div class="amazon-footer-ad">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="70"><br>
                    <b>💡 ترشيحنا لك:</b> {rec_text}<br>
                    <a href="{p_link}" target="_blank" style="color:#0066c0; text-decoration:none; font-weight:bold;">تسوّق عروض اليوم من أمازون 🛒</a>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("❌ لم نجد هذا المكان، جرب كتابة اسم المدينة والمحافظة.")
else:
    apply_live_effects("clear", 20) # الثيم الافتراضي
