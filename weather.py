import streamlit as st
import requests
import pandas as pd

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide")

# 2. الأمان: جلب المفتاح من Secrets
try:
    API_KEY = st.secrets["API_KEY"]
except:
    API_KEY = "e86f7174a5a78c6cde9aec1d0cf46126"

# 3. دالة جلب البيانات (الحالية + التوقعات لنسبة المطر)
@st.cache_data(ttl=600)
def get_weather(city):
    try:
        curr_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        fore_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
        curr_r = requests.get(curr_url).json()
        fore_r = requests.get(fore_url).json()
        return curr_r, fore_r
    except:
        return None, None

# 4. CSS لتنسيق الموبايل والإعلانات
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; }
    .metric-box {
        background: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .ad-banner {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(10px);
        color: white;
        text-align: center;
        padding: 10px;
        z-index: 999;
        font-size: 14px;
    }
    input { color: black !important; }
    </style>
    """, unsafe_allow_html=True)

# 5. الواجهة
st.title("🌤️ Weather Pro Max")
city = st.text_input("Enter City Name:", "Alexandria")

curr, fore = get_weather(city)

if curr and "main" in curr:
    # حساب نسبة المطر من التوقعات
    rain_chance = fore['list'][0].get('pop', 0) * 100 if fore else 0
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-box'><h3>الحرارة</h3><h2>{curr['main']['temp']}°C</h2></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-box'><h3>الرياح</h3><h2>{curr['wind']['speed']}m/s</h2></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-box'><h3>الرطوبة</h3><h2>{curr['main']['humidity']}%</h2></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-box'><h3>احتمال مطر</h3><h2>{int(rain_chance)}%</h2></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.map(pd.DataFrame({'lat': [curr['coord']['lat']], 'lon': [curr['coord']['lon']]}))

# 6. بنر الإعلانات (الربح)
st.markdown("""
    <div class="ad-banner">
        🔥 عرض خاص: احصل على مظلة مطر ذكية الآن بخصم 30%! 
        <a href="https://www.amazon.com" target="_blank" style="color: #00d2ff; text-decoration: none; font-weight: bold;"> اضغط هنا للشراء 🛒</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br><center>Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
