import streamlit as st
import requests
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Weather Pro Max", 
    page_icon="🌤️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. جلب المفاتيح من Secrets
if "OPENWEATHER_API_KEY" not in st.secrets:
    st.error("Missing API Key!")
    st.stop()

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- القاموس ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Type City Name...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind", "humidity": "Humidity",
        "shop": "Shop Deals on Amazon 🛒", "alert": "⚠️ Alert:"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "اكتب اسم المدينة...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "shop": "تسوق عروض أمازون 🛒", "alert": "⚠️ تنبيه:"
    }
}
T = texts[st.session_state.lang]

# --- دوال البحث والطقس (أداء عالي) ---
@st.cache_data(ttl=3600)
def search_city(query):
    try:
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=1&appid={API_KEY}"
        res = requests.get(geo_url).json()
        return (res[0]['lat'], res[0]['lon'], res[0]['name']) if res else (None, None, None)
    except: return None, None, None

@st.cache_data(ttl=600)
def get_weather(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        return requests.get(url).json()
    except: return None

# --- واجهة مستخدم سريعة وخفيفة (بدون لاج) ---
def apply_ui_clean(cond, temp):
    cond = cond.lower()
    # اختيار لون الخلفية حسب الجو (Linear Gradients)
    if "rain" in cond: bg = "linear-gradient(180deg, #203a43, #2c5364)"
    elif "clear" in cond: bg = "linear-gradient(180deg, #2980b9, #6dd5fa)"
    elif temp > 35: bg = "linear-gradient(180deg, #ff512f, #dd2476)"
    else: bg = "linear-gradient(180deg, #0f2027, #203a43, #2c5364)"

    st.markdown(f"""
        <style>
        /* إخفاء تام لعناصر ستريم ليت */
        #MainMenu, footer, header, .stAppDeployButton, #viewerBadge, [data-testid="bundleHostBadge"] {{visibility: hidden !important; display: none !important;}}
        
        .stApp {{
            background: {bg} !important;
            color: white !important;
        }}
        
        .block-container {{padding-top: 2rem;}}
        
        /* تحسين شكل الكروت لتقليل استهلاك الرام */
        [data-testid="stMetric"] {{
            background: rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255,255,255,0.1);
            backdrop-filter: blur(5px);
        }}
        
        .stTextInput input {{ border-radius: 10px !important; border: 1px solid rgba(255,255,255,0.3) !important; background: rgba(0,0,0,0.2) !important; color: white !important; }}
        .stButton button {{ background: white !important; color: black !important; border-radius: 10px !important; width: 100% !important; border: none !important; font-weight: bold !important; }}
        h1, h2 {{ text-align: center !important; font-family: 'sans-serif'; }}
        </style>
    """, unsafe_allow_html=True)

# --- التنفيذ ---
apply_ui_clean("default", 25) # حالة افتراضية
st.markdown(f"<h1>{T['title']}</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 0.6, 1])
with c2:
    if st.button("🌐 AR/EN"):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

query = st.text_input("", placeholder=T["search_place"], key="search_input", label_visibility="collapsed")
analyze_btn = st.button(T["btn_analyze"])

if query:
    lat, lon, name = search_city(query)
    if lat:
        data = get_weather(lat, lon)
        if data:
            apply_ui_clean(data['weather'][0]['main'], data['main']['temp'])
            st.markdown(f"<h2>{name}</h2>", unsafe_allow_html=True)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{data['main']['temp']}°C")
            m2.metric(T["clouds"], f"{data['clouds']['all']}%")
            m3.metric(T["wind"], f"{data['wind']['speed']} m/s")
            m4.metric(T["humidity"], f"{data['main']['humidity']}%")
            
            if analyze_btn:
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=9)
            
            # زر أمازون السريع
            st.markdown(f'''
                <div style="background:#ff9900; padding:12px; border-radius:10px; text-align:center; margin-top:20px;">
                    <a href="https://www.amazon.eg/s?k=weather+station&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:black; font-weight:bold;">{T["shop"]}</a>
                </div>
            ''', unsafe_allow_html=True)
    else:
        st.error("City not found!")

st.markdown(f"<p style='text-align:center; opacity:0.5; margin-top:50px;'>Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
