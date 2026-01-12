import streamlit as st
import requests
import pandas as pd
from deep_translator import GoogleTranslator
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- القاموس اللغوي ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Search city or village...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind Speed", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "ابحث عن مدينة أو قرية...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق عروض أمازون 🛒"
    }
}
T = texts[st.session_state.lang]

# --- وظيفة جلب البيانات (محدثة لدعم العربي) ---
@st.cache_data(ttl=600)
def get_weather(city_name):
    try:
        # البحث عن المدينة بالاسم (بيدعم كل اللغات)
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()
        if res.get("cod") == 200:
            return res
        return None
    except:
        return None

# --- محرك الجرافيكس (Atmospheric Engine) ---
def apply_weather_engine(condition, temp):
    condition = condition.lower()
    if "rain" in condition or "drizzle" in condition:
        p_color, p_w, p_h, p_speed, p_count = "#4facfe", "2px", "30px", "0.8s", 60
    elif "snow" in condition or temp <= 2:
        p_color, p_w, p_h, p_speed, p_count = "#ffffff", "8px", "8px", "5s", 50
    elif "clear" in condition:
        p_color, p_w, p_h, p_speed, p_count = "#ffeb3b", "150px", "150px", "12s", 6
    else:
        p_color, p_w, p_h, p_speed, p_count = "#94a3b8", "3px", "3px", "7s", 30

    particles_html = "".join([ 
        f'<div class="particle" style="left:{random.randint(0, 100)}%; animation-delay:-{random.uniform(0, 10)}s;"></div>' 
        for i in range(p_count) 
    ])

    st.markdown(f"""
        <style>
        .stApp {{ background: transparent !important; }}
        .weather-bg-fixed {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: radial-gradient(circle at center, #1a1a1c 0%, #000 100%);
            z-index: -1; overflow: hidden;
        }}
        .particle {{
            position: absolute; background: {p_color};
            width: {p_w}; height: {p_h};
            opacity: {"0.15" if "clear" in condition else "0.5"};
            border-radius: {"50%" if "rain" not in condition else "0%"};
            filter: {"blur(50px)" if "clear" in condition else "none"};
            animation: fall {p_speed} linear infinite;
        }}
        @keyframes fall {{
            0% {{ transform: translateY(-20vh); }}
            100% {{ transform: translateY(110vh); }}
        }}
        .stTextInput {{ max-width: 450px !important; margin: 0 auto !important; }}
        .stTextInput input {{
            background: white !important; color: #111 !important;
            border-radius: 12px !important; text-align: center;
            border: 3px solid {p_color if "clear" not in condition else "#ff9900"} !important;
            font-weight: bold;
        }}
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(15px); border-radius: 20px !important;
            padding: 20px !important; display: flex !important;
            flex-direction: column !important; align-items: center !important;
        }}
        [data-testid="stMetricValue"] {{ 
            color: {p_color if "clear" not in condition else "#ffeb3b"} !important; 
            font-size: 2.2rem !important; text-align: center !important;
        }}
        [data-testid="stMetricLabel"] {{ text-align: center !important; color: #bbb !important; }}
        .stButton {{ display: flex; justify-content: center; }}
        .stButton button {{
            background: {p_color if "clear" not in condition else "#ff9900"} !important;
            color: #000 !important; font-weight: bold !important;
            border-radius: 10px !important; padding: 10px 40px !important;
        }}
        .amazon-card {{
            background: white; color: #232f3e; padding: 20px;
            border-radius: 20px; text-align: center;
            margin: 40px auto; max-width: 450px;
        }}
        h1, h2 {{ text-align: center !important; color: white !important; }}
        </style>
        <div class="weather-bg-fixed">{particles_html}</div>
    """, unsafe_allow_html=True)

# --- واجهة التطبيق ---
st.markdown(f"<h1>{T['title']}</h1>", unsafe_allow_html=True)

l1, l2, l3 = st.columns([4.5, 1, 4.5])
with l2:
    if st.button("🌐 AR/EN", use_container_width=True):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

query = st.text_input("📍", placeholder=T["search_place"], key="city_input", label_visibility="collapsed")

b1, b2, b3 = st.columns([1, 1.2, 1])
with b2: analyze_click = st.button(T["btn_analyze"], use_container_width=True)

if query:
    # دلوقتي البحث شغال عربي وإنجليزي بطلاقة
    data = get_weather(query)
    if data:
        cond = data['weather'][0]['main'].lower()
        temp = data['main']['temp']
        apply_weather_engine(cond, temp)
        
        # ترجمة اسم المدينة للعرض فقط
        tr = GoogleTranslator(source='auto', target='ar' if st.session_state.lang=="AR" else 'en')
        st.markdown(f"<h2>{tr.translate(data['name'])}</h2>", unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(T["temp"], f"{temp}°C")
        m2.metric(T["clouds"], f"{data['clouds']['all']}%")
        m3.metric(T["wind"], f"{data['wind']['speed']} m/s")
        m4.metric(T["humidity"], f"{data['main']['humidity']}%")

        if analyze_click:
            st.map(pd.DataFrame({'lat': [data['coord']['lat']], 'lon': [data['coord']['lon']]}), zoom=11)

        p_cat = "umbrella" if "rain" in cond else "winter+boots" if temp < 5 else "sunglasses"
        st.markdown(f"""<div class="amazon-card">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="80"><br>
            <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold;">{T['shop']}</a>
        </div>""", unsafe_allow_html=True)
    else:
        st.error("المدينة غير موجودة، جرب كتابتها بشكل صحيح")
else:
    apply_weather_engine("clear", 25)

st.markdown(f"<p style='text-align:center; opacity:0.3; margin-top:50px;'>Created by: Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
