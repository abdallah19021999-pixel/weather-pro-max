import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

# --- Manage Language Session ---
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- Translation Dictionary ---
texts = {
    "EN": {
        "title": "🌤️ Weather Pro Max",
        "search_label": "📍 Location Search (Village/City):",
        "search_place": "e.g. Tanta, Borg El Arab...",
        "btn_analyze": "Explore Local Analysis & Map",
        "temp": "Temperature",
        "clouds": "Clouds",
        "wind": "Wind Speed",
        "humidity": "Humidity",
        "error": "Location not found. Try Village + Province.",
        "warning": "Please search for a location first!",
        "rec_label": "Weather Recommendation:",
        "rec_msg": "Stay prepared with top products for this weather.",
        "shop": "Shop Deals on Amazon 🛒"
    },
    "AR": {
        "title": "🌤️ وذر برو ماكس",
        "search_label": "📍 ابحث عن مكان (قرية/مدينة):",
        "search_place": "مثلاً: طنطا، برج العرب، نجع كذا...",
        "btn_analyze": "عرض التحليل التفصيلي والخريطة",
        "temp": "درجة الحرارة",
        "clouds": "نسبة الغيوم",
        "wind": "سرعة الرياح",
        "humidity": "نسبة الرطوبة",
        "error": "لم يتم العثور على الموقع. حاول كتابة اسم القرية والمحافظة.",
        "warning": "من فضلك ابحث عن مكان أولاً!",
        "rec_label": "ترشيح الطقس:",
        "rec_msg": "كن مستعداً مع أفضل المنتجات لهذا الجو.",
        "shop": "تسوق العروض على أمازون 🛒"
    }
}

T = texts[st.session_state.lang]

# --- Logic: Search & Weather ---
@st.cache_data(ttl=3600)
def get_coordinates(location_name, target_lang):
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
        headers = {'User-Agent': 'WeatherApp_2026_Final'}
        res = requests.get(url, headers=headers, timeout=10).json()
        if res:
            lat, lon = float(res[0]['lat']), float(res[0]['lon'])
            raw_name = res[0]['display_name']
            # Translate display name based on app language
            dest_lang = 'en' if target_lang == "EN" else 'ar'
            display_name = GoogleTranslator(source='auto', target=dest_lang).translate(raw_name)
            return lat, lon, display_name
        return None, None, None
    except: return None, None, None

@st.cache_data(ttl=600)
def get_weather_by_coords(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- UI Header & Style ---
def apply_visuals(condition="clear", temp=25):
    bg = "linear-gradient(to bottom, #1e3c72, #2a5298)"
    overlay = ""
    if "rain" in condition:
        bg = "linear-gradient(to bottom, #203a43, #2c5364)"
        overlay = '<div style="position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:0; pointer-events:none; background: url(\'https://raw.githubusercontent.com/fomantic/Fomantic-UI/master/test/visual/assets/images/rain.png\'); opacity: 0.2; animation: rain_m 0.5s linear infinite;"></div><style>@keyframes rain_m { from {background-position: 0 0;} to {background-position: 40px 400px;} }</style>'
    elif temp > 28:
        bg = "linear-gradient(135deg, #FF8C00 0%, #FFD700 100%)"
        overlay = '<div style="position:fixed; top:-100px; right:-100px; width:450px; height:450px; background:radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%); z-index:0; pointer-events:none;"></div>'

    st.markdown(f"""
        <style>
        .stApp {{ background: {bg}; transition: all 1s ease; color: white; }}
        [data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(5px); border-radius: 12px; }}
        .main-card {{ background: rgba(0, 0, 0, 0.3); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); margin-top:15px; }}
        .amazon-footer {{ background: white; color: #232f3e; padding: 15px; border-radius: 15px; text-align: center; margin-top: 50px; border-bottom: 5px solid #ff9900; max-width: 500px; margin: 0 auto; }}
        .lang-btn {{ position: absolute; top: 10px; right: 10px; }}
        </style>
        {overlay}
        """, unsafe_allow_html=True)

# --- Top Header with Language Toggle ---
h_col1, h_col2 = st.columns([8, 1])
with h_col1:
    st.markdown(f"<h1>{T['title']}</h1>", unsafe_allow_html=True)
with h_col2:
    if st.button("🌐 AR/EN"):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

# --- Search Section ---
search_query = st.text_input(T["search_label"], placeholder=T["search_place"])

col1, col2, col3 = st.columns([1,1,1])
with col2:
    analyze_click = st.button(T["btn_analyze"], use_container_width=True)

if search_query:
    lat, lon, display_name = get_coordinates(search_query, st.session_state.lang)
    if lat:
        weather = get_weather_by_coords(lat, lon)
        if weather:
            cond = weather['weather'][0]['main'].lower()
            temp = weather['main']['temp']
            apply_visuals(cond, temp)

            anim_urls = {"rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
                         "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json"}
            anim = load_lottieurl(anim_urls.get(cond, "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json"))
            if anim: st_lottie(anim, height=180, key="weather_anim")

            st.markdown(f"<h3 style='text-align:center;'>{display_name}</h3>", unsafe_allow_html=True)

            if analyze_click:
                st.markdown("<div class='main-card'>", unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric(T["temp"], f"{temp}°C")
                m2.metric(T["clouds"], f"{weather['clouds']['all']}%")
                m3.metric(T["wind"], f"{weather['wind']['speed']} m/s")
                m4.metric(T["humidity"], f"{weather['main']['humidity']}%")
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=12)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.error(T["error"])
else:
    apply_visuals()
    if analyze_click: st.warning(T["warning"])

# --- Amazon Smart Footer ---
p_cat = "sunglasses" if search_query and 'temp' in locals() and temp > 28 else "umbrella" if search_query and "rain" in cond else "winter+jacket"
st.markdown(f"<br><br><center style='color:white; opacity:0.6;'>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
st.markdown(f"""
    <div class="amazon-footer">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="70"><br>
        <p style="margin:5px 0; font-weight:bold;">{T['rec_label']}</p>
        <p>{T['rec_msg']}</p>
        <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold;">{T['shop']}</a>
    </div>
""", unsafe_allow_html=True)
