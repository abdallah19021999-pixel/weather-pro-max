import streamlit as st
import requests
import pandas as pd
from deep_translator import GoogleTranslator

# 1. Page Config
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- Translations ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Search city or village...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind Speed", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒", "warn_search": "Please search for a city first!"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "ابحث عن مدينة أو قرية...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق على أمازون 🛒", "warn_search": "من فضلك ابحث عن مدينة أولاً!"
    }
}
T = texts[st.session_state.lang]

# --- Functions ---
@st.cache_data(ttl=600)
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()
        return res if res.get("cod") == 200 else None
    except: return None

# --- محرك التأثيرات الجوية الدائم والتنسيق المظبوط ---
def apply_style_engine(condition, temp):
    condition = condition.lower()
    # برمجة أنواع الجو
    if "rain" in condition or "drizzle" in condition:
        p_color, p_w, p_h, p_speed, p_count = "#4facfe", "2px", "30px", "0.7s", 40 # مطر
    elif "snow" in condition or temp <= 2:
        p_color, p_w, p_h, p_speed, p_count = "#ffffff", "8px", "8px", "4s", 50   # ثلج
    elif "clear" in condition:
        p_color, p_w, p_h, p_speed, p_count = "#ffeb3b", "150px", "150px", "10s", 4 # شمس
    else:
        p_color, p_w, p_h, p_speed, p_count = "#94a3b8", "3px", "3px", "6s", 30   # غيوم/رماد

    st.markdown(f"""
        <style>
        /* الأساسيات */
        .stApp {{ background-color: #0f172a !important; color: white !important; }}
        
        /* طبقة الجو الثابتة في الخلفية */
        .weather-bg {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1; pointer-events: none; overflow: hidden;
            background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
        }}
        
        .particle {{
            position: absolute; background: {p_color};
            width: {p_w}; height: {p_h};
            opacity: {"0.1" if "clear" in condition else "0.4"};
            border-radius: {"50%" if "rain" not in condition else "0%"};
            filter: {"blur(60px)" if "clear" in condition else "none"};
            animation: fall {p_speed} linear infinite;
        }}

        @keyframes fall {{
            from {{ transform: translateY(-20vh) translateX(0); }}
            to {{ transform: translateY(120vh) translateX(40px); }}
        }}

        /* توسيط البحث والمدخلات */
        .stTextInput {{ max-width: 700px; margin: 0 auto; }}
        .stTextInput input {{
            background: white !important; color: #1e293b !important;
            border-radius: 15px !important; text-align: center;
            border: 4px solid {p_color if "clear" not in condition else "#ff9900"} !important;
            font-size: 1.2rem !important; font-weight: bold;
        }}

        /* توسيط المربعات (الزوايا المظبوطة) */
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px);
            border-radius: 20px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            padding: 20px !important;
            display: flex !important; flex-direction: column !important;
            align-items: center !important; justify-content: center !important;
        }}
        [data-testid="stMetricValue"] {{ 
            color: {p_color if "clear" not in condition else "#ffeb3b"} !important; 
            font-size: 2.6rem !important; text-align: center !important; width: 100%;
        }}
        [data-testid="stMetricLabel"] {{ 
            color: #cbd5e1 !important; font-size: 1.1rem !important;
            text-align: center !important; width: 100%;
        }}

        /* الزرار موسط */
        .stButton {{ display: flex; justify-content: center; }}
        .stButton button {{
            background: {p_color if "clear" not in condition else "#ff9900"} !important;
            color: #0f172a !important; font-weight: bold !important;
            border-radius: 12px !important; padding: 10px 50px !important;
        }}

        /* كارت أمازون الموسط */
        .footer-amazon {{
            background: white; color: #232f3e; padding: 25px;
            border-radius: 25px; text-align: center;
            margin: 50px auto; max-width: 500px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.4);
        }}
        
        h1, h2 {{ text-align: center !important; width: 100%; }}
        </style>
        
        <div class="weather-bg">
            {" ".join([f'<div class="particle" style="left:{i*(100/p_count)}%; animation-delay:{i*0.3}s"></div>' for i in range(p_count)])}
        </div>
    """, unsafe_allow_html=True)

# --- Layout ---
st.markdown(f"<h1>{T['title']}</h1>", unsafe_allow_html=True)

# زرار اللغة
c1, c2, c3 = st.columns([4.5, 1, 4.5])
with c2:
    if st.button("🌐 AR/EN"):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

# صندوق البحث
query = st.text_input("📍", placeholder=T["search_place"], label_visibility="collapsed")

# زرار التحليل
bc1, bc2, bc3 = st.columns([1, 1.5, 1])
with bc2: analyze_click = st.button(T["btn_analyze"], use_container_width=True)

if query:
    data = get_weather(query)
    if data:
        cond = data['weather'][0]['main'].lower()
        temp = data['main']['temp']
        
        # تشغيل المحرك الجوي
        apply_style_engine(cond, temp)
        
        # ترجمة اسم المدينة
        tr = GoogleTranslator(source='auto', target='ar' if st.session_state.lang=="AR" else 'en')
        city_display = tr.translate(data['name'])
        
        st.markdown(f"<h2>{city_display}</h2>", unsafe_allow_html=True)
        
        # Metrics موسطة تماماً
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(T["temp"], f"{temp}°C")
        m2.metric(T["clouds"], f"{data['clouds']['all']}%")
        m3.metric(T["wind"], f"{data['wind']['speed']} m/s")
        m4.metric(T["humidity"], f"{data['main']['humidity']}%")

        if analyze_click:
            st.markdown("<br>", unsafe_allow_html=True)
            st.map(pd.DataFrame({'lat': [data['coord']['lat']], 'lon': [data['coord']['lon']]}), zoom=11)

        # Footer Amazon
        p_cat = "snow+boots" if temp <= 2 else "umbrella" if "rain" in cond else "sunglasses"
        st.markdown(f"""<div class="footer-amazon">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="90"><br>
            <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold; font-size:1.2rem;">{T['shop']}</a>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; opacity:0.4;'>Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
    else:
        st.error("City not found. Please check the name.")
else:
    # الحالة الافتراضية (شمس هادئة)
    apply_style_engine("clear", 25)
    if analyze_click:
        st.warning(T["warn_search"])
