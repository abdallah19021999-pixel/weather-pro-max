import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

# استدعاء الأسرار (التوكنات)
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# --- رابط الأفلييت الخاص بك بعد ما فعلت الحساب ---
# تم تحديث الكود بـ Store ID الخاص بك: abdallah2026-21
AMAZON_BASE_URL = "https://www.amazon.eg/?&tag=abdallah2026-21" 

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

# --- الـ CSS للتنسيق ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background: linear-gradient(to bottom, #1e3c72, #2a5298); color: white; }}
    .amazon-ad-box {{
        background: #ffffff; color: #232f3e; padding: 20px; border-radius: 15px;
        text-align: center; margin-top: 30px; border-bottom: 5px solid #ff9900;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }}
    .ad-button {{
        background-color: #ff9900; color: white !important; padding: 10px 25px;
        text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block; margin-top: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

st.title("🌤️ Weather Pro Max Dashboard")

city = st.text_input("Enter City Name:", "Alexandria")
weather_data = get_weather_data(city)

if weather_data:
    main_cond = weather_data['weather'][0]['main'].lower()
    temp = weather_data['main']['temp']
    
    # تحديد المنتج حسب الجو
    if "rain" in main_cond:
        ad_text = "☔ الدنيا بتمطر؟ الحق عروض الشماسي والملابس المضادة للمطر!"
        product_link = "https://www.amazon.eg/s?k=umbrella&tag=abdallah2026-21"
    elif temp > 25:
        ad_text = "🕶️ الجو شمس؟ احمي عينك بأفضل نظارات الشمس من أمازون!"
        product_link = "https://www.amazon.eg/s?k=sunglasses&tag=abdallah2026-21"
    elif temp < 15:
        ad_text = "🧥 الجو برد؟ شوف جواكت الشتاء الجديدة والدفايات!"
        product_link = "https://www.amazon.eg/s?k=winter+jackets&tag=abdallah2026-21"
    else:
        ad_text = "🎒 الجو مناسب للخروج! شوف أحدث عروض شنط الظهر والرحلات!"
        product_link = "https://www.amazon.eg/s?k=backpacks&tag=abdallah2026-21"

    # الأنميشن
    anim_urls = {"rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
                 "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
                 "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json",
                 "default": "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"}
    
    anim_json = load_lottieurl(anim_urls.get(main_cond if main_cond in anim_urls else "default"))
    if anim_json: st_lottie(anim_json, height=250)

    # زر التحليل
    if st.button("Show Weather Analysis"):
        notify_me(f"💰 كليك على إعلان أمازون! بحث عن {city}")
        st.markdown("---")
        c1, c2 = st.columns(2)
        c1.metric("Temp", f"{temp} °C")
        c2.metric("Clouds", f"{weather_data['clouds']['all']}%")
        st.map(pd.DataFrame({'lat': [weather_data['coord']['lat']], 'lon': [weather_data['coord']['lon']]}))

    # شريط إعلان أمازون الربحي
    st.markdown(f"""
        <div class="amazon-ad-box">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="100"><br>
            <p style="color: #232f3e; margin: 10px 0;">{ad_text}</p>
            <a href="{product_link}" target="_blank" class="ad-button">تسوق الآن بخصم خاص 🛒</a>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br><center>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
