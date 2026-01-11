import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie

# 1. إعدادات الصفحة - جعلها مريحة للموبايل
st.set_page_config(
    page_title="Weather Pro", 
    page_icon="🌤️", 
    layout="centered", # التوسيط أفضل للموبايل
    initial_sidebar_state="collapsed"
)

# دالة تحميل الأنميشن
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception: return None

# روابط الأنميشن
LOTTIE_URLS = {
    "rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
    "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
    "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json",
    "snow": "https://lottie.host/1c71dd3a-86c5-47e0-9173-0985c572a0f8/R1000N738P.json",
    "default": "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"
}

# 2. جلب البيانات
@st.cache_data(ttl=600)
def get_weather_data(city_name):
    API_KEY = "e86f7174a5a78c6cde9aec1d0cf46126"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- المعالجة ---
city = st.text_input("Enter City Name:", "Alexandria")
weather_data = get_weather_data(city)

# تحديد الحالة والخلفية
current_condition = "default"
bg_color = "linear-gradient(to bottom, #1e3c72, #2a5298)"

if weather_data:
    main_cond = weather_data['weather'][0]['main'].lower()
    if "rain" in main_cond: 
        current_condition, bg_color = "rain", "linear-gradient(to bottom, #203a43, #2c5364)"
    elif "clear" in main_cond: 
        current_condition, bg_color = "clear", "linear-gradient(to bottom, #2980b9, #6dd5fa)"
    elif "cloud" in main_cond: 
        current_condition, bg_color = "clouds", "linear-gradient(to bottom, #bdc3c7, #2c3e50)"
    elif "snow" in main_cond: 
        current_condition, bg_color = "snow", "linear-gradient(to bottom, #a7d0e4, #e0eafc)"

# تطبيق الـ CSS المخصص للموبايل
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background: {bg_color}; color: white; transition: background 0.5s ease; }}
    
    /* تعديلات الموبايل */
    .stTextInput > div > div > input {{
        border-radius: 20px !important;
        text-align: center !important;
    }}
    
    div.stButton > button {{
        background-color: #ffffff; 
        color: #1e3c72; 
        border-radius: 20px;
        width: 100%; 
        font-weight: bold; 
        border: none; 
        height: 3.5em;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
    }}

    /* تحسين شكل المتركس في الموبايل */
    [data-testid="stMetric"] {{
        background: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 15px;
        text-align: center;
    }}
    
    h1 {{ font-size: 1.8rem !important; text-align: center; }}
    </style>
    """, unsafe_allow_html=True)

st.title("🌤️ Weather Pro Max")

# عرض الأنميشن بحجم مناسب للموبايل
anim_json = load_lottieurl(LOTTIE_URLS.get(current_condition, LOTTIE_URLS["default"]))
if anim_json:
    st_lottie(anim_json, height=200, key="weather_anim")

# زر التقرير
if st.button("Get Detailed Report"):
    if weather_data:
        st.markdown("---")
        # في الموبايل، الكولمز بتنزل تحت بعضها تلقائياً بشكل جميل
        c1, c2, c3 = st.columns(3)
        c1.metric("Temp", f"{weather_data['main']['temp']} °C")
        c2.metric("Wind", f"{weather_data['wind']['speed']} m/s")
        c3.metric("Humidity", f"{weather_data['main']['humidity']}%")
        
        st.markdown("---")
        # الخريطة
        st.map(pd.DataFrame({'lat': [weather_data['coord']['lat']], 'lon': [weather_data['coord']['lon']]}))
        
        # الأيقونة والوصف
        icon_code = weather_data['weather'][0]['icon']
        st.image(f"http://openweathermap.org/img/wn/{icon_code}@4x.png")
        st.write(f"Condition: {weather_data['weather'][0]['description'].capitalize()}")
    else:
        st.error("City not found!")

st.markdown("<br><center style='font-size:0.8em; opacity:0.7;'>Abdallah Nabil | 2026</center>", unsafe_allow_html=True)