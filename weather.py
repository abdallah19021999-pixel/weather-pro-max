import streamlit as st
import requests
import pandas as pd
import random

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="Weather Pro Max", 
    page_icon="🌤️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. التحقق من مفتاح الـ API
if "OPENWEATHER_API_KEY" not in st.secrets:
    st.error("Missing API Key in Secrets!")
    st.stop()

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

# حالة اللغة
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- القاموس العربي والإنجليزي ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Type City Name (e.g. Cairo)...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind Speed", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒", "alert": "⚠️ Safety Alert:"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "اكتب اسم المدينة (مثلاً: القاهرة)...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق عروض أمازون 🛒", "alert": "⚠️ تنبيه للسلامة:"
    }
}
T = texts[st.session_state.lang]

# --- محرك البحث الجغرافي ---
@st.cache_data(ttl=3600)
def search_city(query):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=1&appid={API_KEY}"
        res = requests.get(geo_url).json()
        if res:
            return res[0]['lat'], res[0]['lon'], res[0]['name']
        return None, None, None
    except:
        return None, None, None

@st.cache_data(ttl=600)
def get_weather(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        return requests.get(url).json()
    except: return None

# --- وظيفة تحسين الواجهة وإخفاء كل عناصر ستريم ليت ---
def apply_ui(cond, temp, data):
    # تحديد ألوان الجزيئات حسب الطقس
    cond = cond.lower()
    if "rain" in cond: p_color, p_speed = "#4facfe", "0.8s"
    elif "snow" in cond or temp <= 2: p_color, p_speed = "#ffffff", "5s"
    elif "clear" in cond: p_color, p_speed = "#ffeb3b", "12s"
    else: p_color, p_speed = "#94a3b8", "7s"

    # إنشاء جزيئات متحركة
    particles = "".join([f'<div class="particle" style="left:{random.randint(0, 100)}%; animation-delay:-{random.uniform(0, 10)}s;"></div>' for i in range(50)])
    
    # رسالة التنبيه الذكية
    alert_html = ""
    if data['wind']['speed'] > 10 or "rain" in cond or temp > 38:
        msg = "انتبه من تقلبات الجو!" if st.session_state.lang == "AR" else "Watch out for weather changes!"
        alert_html = f'<div style="background:rgba(255,75,75,0.2); border:2px solid #ff4b4b; padding:15px; border-radius:12px; text-align:center; margin-bottom:20px; color:white; font-weight:bold;">{T["alert"]} {msg}</div>'

    # الكود السحري لإخفاء كل شيء وجعل الخلفية متحركة
    st.markdown(f"""
        <style>
        /* إخفاء القائمة، التذييل، الهيدر، وعلامات Deploy الحمراء والزرقاء */
        #MainMenu {{visibility: hidden !important;}}
        footer {{visibility: hidden !important;}}
        header {{visibility: hidden !important;}}
        .stAppDeployButton {{display: none !important;}}
        #viewerBadge {{display: none !important;}}
        [data-testid="bundleHostBadge"] {{display: none !important;}}
        [data-testid="stStatusWidget"] {{display: none !important;}}
        
        /* تجميل الحاوية */
        .block-container {{padding-top: 2rem; padding-bottom: 0rem;}}

        /* الخلفية المتحركة والجزيئات */
        .stApp {{ background: transparent !important; }}
        .bg {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: radial-gradient(circle at center, #111 0%, #000 100%); z-index: -1; overflow: hidden; }}
        .particle {{ position: absolute; background: {p_color}; width: 2px; height: 20px; opacity: 0.4; animation: fall {p_speed} linear infinite; }}
        @keyframes fall {{ 0% {{ transform: translateY(-10vh); }} 100% {{ transform: translateY(110vh); }} }}
        
        /* تنسيق المدخلات والأزرار */
        .stTextInput input {{ border-radius: 12px !important; text-align: center; border: 2px solid {p_color} !important; background: rgba(255,255,255,0.05) !important; color: white !important; }}
        [data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.05) !important; backdrop-filter: blur(15px); border-radius: 15px !important; padding: 15px !important; text-align: center !important; border: 1px solid rgba(255,255,255,0.1); }}
        .stButton button {{ background: {p_color} !important; color: black !important; font-weight: bold !important; width: 100% !important; border-radius: 12px !important; border: none !important; transition: 0.3s; }}
        .stButton button:hover {{ transform: scale(1.02); background: white !important; }}
        h1, h2 {{ text-align: center !important; color: white !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        </style>
        <div class="bg">{particles}</div>
    """, unsafe_allow_html=True)
    return alert_html

# --- تنفيذ واجهة المستخدم ---
st.markdown(f"<h1>{T['title']}</h1>", unsafe_allow_html=True)

# تبديل اللغة
c1, c2, c3 = st.columns([1, 0.6, 1])
with c2:
    if st.button("🌐 AR/EN", key="lang_toggle"):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

# محرك البحث
query = st.text_input("📍", placeholder=T["search_place"], key="search_input", label_visibility="collapsed")
analyze_btn = st.button(T["btn_analyze"], key="analyze_btn")

if query:
    lat, lon, name = search_city(query)
    if lat:
        data = get_weather(lat, lon)
        if data:
            # تطبيق الجرافيكس والتنبيهات
            alert_box = apply_ui(data['weather'][0]['main'], data['main']['temp'], data)
            st.markdown(f"<h2>{name}</h2>", unsafe_allow_html=True)
            st.markdown(alert_box, unsafe_allow_html=True)
            
            # عرض البيانات الأساسية
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{data['main']['temp']}°C")
            m2.metric(T["clouds"], f"{data['clouds']['all']}%")
            m3.metric(T["wind"], f"{data['wind']['speed']} m/s")
            m4.metric(T["humidity"], f"{data['main']['humidity']}%")
            
            # عرض الخريطة عند الضغط على الزر
            if analyze_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=10)
            
            # رابط الأفلييت (مربع جذاب)
            st.markdown(f'''
                <div style="background:linear-gradient(90deg, #ff9900, #ffcc00); padding:15px; border-radius:15px; text-align:center; margin-top:30px; box-shadow: 0px 4px 15px rgba(255,153,0,0.3);">
                    <a href="https://www.amazon.eg/s?k=weather+station&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#111; font-weight:bold; font-size:18px;">{T["shop"]}</a>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.error("City not found. Please try another name.")
else:
    # شاشة الانتظار الافتراضية بنظام نظيف
    apply_ui("clear", 25, {'wind': {'speed': 0}})

# التوقيع السفلي
st.markdown(f"<p style='text-align:center; opacity:0.3; margin-top:60px; color:white;'>Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
