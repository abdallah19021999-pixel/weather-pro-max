import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie

# 1. إعدادات الصفحة
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide")

# 2. الأمان: جلب المفاتيح من Secrets
# ملاحظة: يجب إضافة API_KEY و TELEGRAM_TOKEN و TELEGRAM_CHAT_ID في إعدادات Streamlit Cloud
try:
    API_KEY = st.secrets["API_KEY"]
    TG_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TG_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except:
    API_KEY = "e86f7174a5a78c6cde9aec1d0cf46126"
    TG_TOKEN = None
    TG_CHAT_ID = None

# دالة إرسال تنبيه تليجرام
def send_telegram_alert(city, rain_chance):
    if TG_TOKEN and TG_CHAT_ID:
        msg = f"⚠️ تنبيه مطر من Weather Pro Max!\n\nمدينة {city} احتمال المطر فيها وصل لـ {int(rain_chance)}% 🌧️. لا تنسَ المظلة!"
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage?chat_id={TG_CHAT_ID}&text={msg}"
        try:
            requests.get(url)
        except:
            pass

# دالة جلب البيانات
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

# 3. واجهة المستخدم والـ CSS
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; }}
    .metric-box {{
        background: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.15);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.2);
    }}
    .ad-banner {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(10px);
        color: white;
        text-align: center;
        padding: 12px;
        z-index: 999;
        font-size: 15px;
        border-top: 1px solid #00d2ff;
    }}
    input {{ color: black !important; font-weight: bold !important; border-radius: 10px !important; }}
    </style>
    """, unsafe_allow_html=True)

st.title("🌤️ Weather Pro Max Dashboard")
city = st.text_input("Enter City Name:", "Alexandria")

curr, fore = get_weather(city)

if curr and "main" in curr:
    # حساب نسبة الأمطار
    rain_chance = fore['list'][0].get('pop', 0) * 100 if fore else 0
    
    # نظام التنبيهات
    if rain_chance > 50:
        send_telegram_alert(city, rain_chance)
        st.warning(f"🚨 تم إرسال تنبيه مطر ({int(rain_chance)}%) إلى تليجرام الخاص بك!")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='metric-box'><h4>Temp</h4><h2>{curr['main']['temp']}°C</h2></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='metric-box'><h4>Wind</h4><h2>{curr['wind']['speed']} m/s</h2></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='metric-box'><h4>Humidity</h4><h2>{curr['main']['humidity']}%</h2></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='metric-box'><h4>Rain Chance</h4><h2>{int(rain_chance)}%</h2></div>", unsafe_allow_html=True)

    st.markdown("---")
    
    # عرض الخريطة
    st.map(pd.DataFrame({'lat': [curr['coord']['lat']], 'lon': [curr['coord']['lon']]}))

# 4. قسم الإعلانات (الربح)
st.markdown("""
    <div class="ad-banner">
        ☔ هل تتوقع أمطاراً؟ اشتري أفضل مظلة ذكية الآن بخصم 30%! 
        <a href="https://www.amazon.com" target="_blank" style="color: #00d2ff; text-decoration: none; font-weight: bold;"> اطلبها الآن 🛒</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br><br><center>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
