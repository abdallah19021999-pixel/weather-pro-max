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
        "title": "Weather Pro Max", "search_place": "Search city...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind Speed", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒", "warn_search": "Search for a city first!"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "ابحث عن مدينة...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق على أمازون 🛒", "warn_search": "ابحث عن مدينة أولاً!"
    }
}
T = texts[st.session_state.lang]

@st.cache_data(ttl=600)
def get_weather(city_name):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
        return requests.get(url).json()
    except: return None

# --- محرك التأثيرات البصرية الدائمة ---
def apply_atmosphere(condition, temp):
    condition = condition.lower()
    
    # تحديد نوع التأثير بناءً على الحالة
    if "rain" in condition or "drizzle" in condition:
        p_color, p_w, p_h, p_speed, p_count = "#4facfe", "2px", "25px", "0.7s", 30 # مطر
    elif "snow" in condition or temp <= 2:
        p_color, p_w, p_h, p_speed, p_count = "#ffffff", "6px", "6px", "5s", 40   # ثلج
    elif "clear" in condition:
        p_color, p_w, p_h, p_speed, p_count = "#ffeb3b", "100px", "100px", "10s", 3 # شمس (وهج)
    else:
        p_color, p_w, p_h, p_speed, p_count = "#ffcc33", "2px", "2px", "8s", 20   # غيوم/رماد

    st.markdown(f"""
        <style>
        .stApp {{ background: #0a0a0b !important; }}
        
        /* طبقة الجرافيكس الثابتة */
        .atmosphere-layer {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            z-index: -1; pointer-events: none; overflow: hidden;
            background: radial-gradient(circle at 50% 50%, #1a1a1c, #000);
        }}
        
        .particle {{
            position: absolute; background: {p_color};
            width: {p_w}; height: {p_h};
            opacity: {"0.1" if "clear" in condition else "0.4"};
            border-radius: {"50%" if "rain" not in condition else "0%"};
            filter: {"blur(40px)" if "clear" in condition else "none"};
            animation: fall {p_speed} linear infinite;
        }}

        @keyframes fall {{
            from {{ transform: translateY(-20vh) translateX(0); }}
            to {{ transform: translateY(120vh) translateX(30px); }}
        }}

        /* تنسيق البحث */
        .stTextInput input {{
            background: white !important; color: black !important;
            border-radius: 12px !important; text-align: center; font-weight: bold;
            border: 3px solid {p_color if "clear" not in condition else "#ff9900"} !important;
        }}
        
        /* تنسيق الـ Metrics */
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255,255,255,0.1); border-radius: 20px;
            text-align: center; display: flex; flex-direction: column; align-items: center;
        }}
        [data-testid="stMetricValue"] {{ color: {p_color if "clear" not in condition else "#ffeb3b"} !important; text-align: center !important; width:100%; }}
        [data-testid="stMetricLabel"] {{ text-align: center !important; width:100%; }}
        </style>
        
        <div class="atmosphere-layer">
            {" ".join([f'<div class="particle" style="left:{i*(100/p_count)}%; animation-delay:{i*0.4}s"></div>' for i in range(p_count)])}
        </div>
    """, unsafe_allow_html=True)

# --- App Layout ---
st.markdown(f"<h1 style='text-align:center;'>{T['title']}</h1>", unsafe_allow_html=True)

# زرار اللغة
c1, c2, c3 = st.columns([4.5, 1, 4.5])
with c2:
    if st.button("🌐 AR/EN"):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

query = st.text_input("📍", placeholder=T["search_place"], label_visibility="collapsed")

b1, b2, b3 = st.columns([1, 1.5, 1])
with b2: analyze = st.button(T["btn_analyze"], use_container_width=True)

if query:
    data = get_weather(query)
    if data and data.get("main"):
        cond = data['weather'][0]['main'].lower()
        temp = data['main']['temp']
        
        # تطبيق التأثير اللحظي والدائم
        apply_atmosphere(cond, temp)
        
        # ترجمة اسم المدينة
        tr = GoogleTranslator(source='auto', target='ar' if st.session_state.lang=="AR" else 'en')
        st.markdown(f"<h2 style='text-align:center;'>{tr.translate(data['name'])}</h2>", unsafe_allow_html=True)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(T["temp"], f"{temp}°C")
        m2.metric(T["clouds"], f"{data['clouds']['all']}%")
        m3.metric(T["wind"], f"{data['wind']['speed']} m/s")
        m4.metric(T["humidity"], f"{data['main']['humidity']}%")

        if analyze:
            st.map(pd.DataFrame({'lat': [data['coord']['lat']], 'lon': [data['coord']['lon']]}), zoom=10)

        # Footer
        p_cat = "snow+boots" if temp <= 2 else "umbrella" if "rain" in cond else "sunglasses"
        st.markdown(f"""<div style="background:white; padding:20px; border-radius:20px; text-align:center; margin-top:50px; max-width:500px; margin-left:auto; margin-right:auto;">
            <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="color:#0066c0; font-weight:bold; text-decoration:none;">{T['shop']}</a>
        </div>""", unsafe_allow_html=True)
    else:
        st.error("City not found")
else:
    apply_atmosphere("clear", 25) # تأثير الشمس الافتراضي
