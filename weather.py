import streamlit as st
import requests
import pandas as pd
from deep_translator import GoogleTranslator
import random

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

# 2. الثوابت (Keys)
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# 3. القاموس اللغوي
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
        "shop": "تسوق عروض أمازون 🛒", "warn_search": "من فضلك ابحث عن مدينة أولاً!"
    }
}
T = texts[st.session_state.lang]

# 4. وظيفة جلب البيانات
@st.cache_data(ttl=600)
def get_weather(city):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()
        return res if res.get("cod") == 200 else None
    except: return None

# 5. محرك التأثيرات الجوية الدائمة (Atmospheric Engine)
def apply_weather_engine(condition, temp):
    condition = condition.lower()
    
    # تحديد المعايير البصرية
    if "rain" in condition or "drizzle" in condition:
        p_color, p_w, p_h, p_speed, p_count = "#4facfe", "2px", "30px", "0.8s", 50 # مطر
    elif "snow" in condition or temp <= 2:
        p_color, p_w, p_h, p_speed, p_count = "#ffffff", "8px", "8px", "5s", 45   # ثلج
    elif "clear" in condition:
        p_color, p_w, p_h, p_speed, p_count = "#ffeb3b", "130px", "130px", "12s", 5 # شمس
    else:
        p_color, p_w, p_h, p_speed, p_count = "#94a3b8", "3px", "3px", "7s", 30   # غيوم/رماد

    # إنشاء الجزيئات ببدء تشغيل عشوائي لضمان الديمومة
    particles_html = "".join([ 
        f'<div class="particle" style="left:{random.randint(0, 100)}%; animation-delay:-{random.uniform(0, 10)}s; animation-duration:{random.uniform(0.8, 1.2)} * {p_speed};"></div>' 
        for i in range(p_count) 
    ])

    st.markdown(f"""
        <style>
        .stApp {{ background-color: #060606 !important; color: white !important; }}
        
        .weather-layer {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            z-index: -1; pointer-events: none; overflow: hidden;
            background: radial-gradient(circle at center, #1a1a1c 0%, #000 100%);
        }}
        
        .particle {{
            position: absolute; background: {p_color};
            width: {p_w}; height: {p_h};
            opacity: {"0.15" if "clear" in condition else "0.4"};
            border-radius: {"50%" if "rain" not in condition else "0%"};
            filter: {"blur(50px)" if "clear" in condition else "none"};
            animation: fall linear infinite;
        }}

        @keyframes fall {{
            0% {{ transform: translateY(-25vh) translateX(0); }}
            100% {{ transform: translateY(125vh) translateX(35px); }}
        }}

        /* تنسيق صندوق البحث */
        .stTextInput {{ max-width: 750px; margin: 0 auto; }}
        .stTextInput input {{
            background: white !important; color: #111 !important;
            border-radius: 15px !important; text-align: center;
            border: 4px solid {p_color if "clear" not in condition else "#ff9900"} !important;
            font-size: 1.3rem !important; font-weight: bold;
        }}

        /* تنسيق الـ Metrics المسطرة */
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(12px); border-radius: 20px !important;
            border: 1px solid rgba(255,255,255,0.1) !important;
            padding: 25px !important; display: flex !important;
            flex-direction: column !important; align-items: center !important;
        }}
        [data-testid="stMetricValue"] {{ 
            color: {p_color if "clear" not in condition else "#ffeb3b"} !important; 
            font-size: 2.8rem !important; text-align: center !important; width: 100%;
        }}
        [data-testid="stMetricLabel"] {{ 
            color: #ccc !important; font-size: 1.1rem !important; text-align: center !important; width: 100%;
        }}

        /* الزرار موسط واحترافي */
        .stButton {{ display: flex; justify-content: center; }}
        .stButton button {{
            background: {p_color if "clear" not in condition else "#ff9900"} !important;
            color: #000 !important; font-weight: bold !important;
            border-radius: 12px !important; padding: 12px 60px !important;
            border: none !important; transition: 0.3s;
        }}
        .stButton button:hover {{ transform: scale(1.05); }}

        /* كارت أمازون */
        .amazon-box {{
            background: white; color: #232f3e; padding: 25px;
            border-radius: 25px; text-align: center;
            margin: 50px auto; max-width: 500px;
            border-bottom: 6px solid #ff9900;
        }}
        </style>
        <div class="weather-layer">{particles_html}</div>
    """, unsafe_allow_html=True)

# 6. هيكل التطبيق
st.markdown(f"<h1>{T['title']}</h1>", unsafe_allow_html=True)

# صف اللغة
c1, c2, c3 = st.columns([4.5, 1, 4.5])
with c2:
    if st.button("🌐 AR/EN", use_container_width=True):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

# البحث والتحليل
query = st.text_input("📍", placeholder=T["search_place"], label_visibility="collapsed")
bc1, bc2, bc3 = st.columns([1, 1.5, 1])
with bc2: analyze_btn = st.button(T["btn_analyze"], use_container_width=True)

if query:
    data = get_weather(query)
    if data:
        cond = data['weather'][0]['main'].lower()
        temp = data['main']['temp']
        apply_weather_engine(cond, temp)
        
        # ترجمة الاسم
        tr = GoogleTranslator(source='auto', target='ar' if st.session_state.lang=="AR" else 'en')
        st.markdown(f"<h2>{tr.translate(data['name'])}</h2>", unsafe_allow_html=True)
        
        # عرض البيانات
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(T["temp"], f"{temp}°C")
        m2.metric(T["clouds"], f"{data['clouds']['all']}%")
        m3.metric(T["wind"], f"{data['wind']['speed']} m/s")
        m4.metric(T["humidity"], f"{data['main']['humidity']}%")

        if analyze_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            st.map(pd.DataFrame({'lat': [data['coord']['lat']], 'lon': [data['coord']['lon']]}), zoom=11)

        # الأفلييت
        p_cat = "winter+boots" if temp <= 5 else "umbrella" if "rain" in cond else "sunglasses"
        st.markdown(f"""<div class="amazon-box">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="100"><br><br>
            <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold; font-size:1.3rem;">{T['shop']}</a>
        </div>""", unsafe_allow_html=True)
    else:
        st.error("City not found!")
else:
    apply_weather_engine("clear", 25)
    if analyze_btn: st.warning(T["warn_search"])

st.markdown(f"<p style='text-align:center; opacity:0.3; margin-top:50px;'>Created by: Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
