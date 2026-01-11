import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

AMAZON_AFFILIATE_URL = "https://www.amazon.com/?tag=abdallahnabil-20" # غير 'abdallahnabil-20' بكودك

def notify_me(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=5)
    except: pass

@st.cache_data(ttl=600)
def get_weather_data(city_name):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(city_name)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={translated}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

def load_lottieurl(url: str):
    try: return requests.get(url).json()
    except: return None

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background: linear-gradient(to bottom, #1e3c72, #2a5298); color: white; }}
    
    .amazon-ad-box {{
        background: #ffffff;
        color: #232f3e;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-top: 30px;
        border-bottom: 5px solid #ff9900;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }}
    .ad-button {{
        background-color: #ff9900;
        color: white !important;
        padding: 10px 25px;
        text-decoration: none;
        border-radius: 25px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
    }}
    
    [data-testid="stMetric"] {{
        background: rgba(255,255,255,0.1);
        padding: 15px !important;
        border-radius: 15px;
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("🌤️ Weather Pro Max Dashboard")

city = st.text_input("Enter City Name:", "Alexandria")
weather_data = get_weather_data(city)

if weather_data:
    main_cond = weather_data['weather'][0]['main'].lower()
    temp = weather_data['main']['temp']
    
    product_name = ""
    ad_text = ""
    
    if "rain" in main_cond:
        product_name = "Umbrellas & Raincoats"
        ad_text = "☔ الجو مطر؟ الحق خصومات الشماسي والجاكيتات الووتر بروف!"
    elif temp > 25:
        product_name = "Sunglasses & Sunscreen"
        ad_text = "🕶️ الجو شمس؟ شوف أحدث نظارات ريبان وعروض الصيف!"
    elif temp < 15:
        product_name = "Winter Jackets & Heaters"
        ad_text = "🧥 الجو برد؟ دفي نفسك مع كولكشن الشتاء الجديد!"
    else:
        product_name = "Backpacks & Travel Gear"
        ad_text = "🎒 الجو مناسب للخروج! شوف شنط الرحلات المميزة!"

    anim_urls = {
        "rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
        "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
        "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json",
        "default": "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"
    }
    anim_json = load_lottieurl(anim_urls.get(main_cond if main_cond in anim_urls else "default"))
    if anim_json: st_lottie(anim_json, height=250)

منظمة للموبايل
    if st.button("Show Weather Analysis"):
        notify_me(f"💰 مستخدم مهتم بـ {city} | الجو {main_cond}")
        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.metric("Temp", f"{temp} °C")
        c2.metric("Clouds", f"{weather_data['clouds']['all']}%")
        
        c3, c4 = st.columns(2)
        c3.metric("Wind", f"{weather_data['wind']['speed']} m/s")
        c4.metric("Humidity", f"{weather_data['main']['humidity']}%")
        
        st.map(pd.DataFrame({'lat': [weather_data['coord']['lat']], 'lon': [weather_data['coord']['lon']]}))

   
    st.markdown(f"""
        <div class="amazon-ad-box">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="100"><br>
            <p style="color: #232f3e; margin: 10px 0;">{ad_text}</p>
            <a href="{AMAZON_AFFILIATE_URL}" class="ad-button">تسوق الآن من أمازون 🛒</a>
            <p style="font-size: 0.7rem; margin-top: 10px; color: #666;">* Weather Pro Max</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><center>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)

