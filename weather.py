import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide")

# 2. جلب مفاتيح الربط من الـ Secrets
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
AFFILIATE_ID = "abdallah2026-21"

# حالة اللغة الافتراضية
if "lang" not in st.session_state:
    st.session_state.lang = "AR"

# --- دالة إرسال تنبيه للتليجرام ---
def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message})
    except: pass

# --- دالة التحذيرات الذكية ---
def get_alert(data, lang):
    temp = data['main']['temp']
    wind = data['wind']['speed']
    condition = data['weather'][0]['main'].lower()
    
    if "rain" in condition or "thunderstorm" in condition:
        return ("⚠️ تنبيه مطر: لا تنسى المظلة!" if lang == "AR" else "⚠️ Rain Alert: Don't forget your umbrella!")
    if temp > 38:
        return ("🔥 موجة حر شديدة: اشرب مياه بكثرة!" if lang == "AR" else "🔥 Heat Wave: Stay hydrated!")
    if wind > 15:
        return ("💨 رياح قوية: كن حذراً أثناء القيادة!" if lang == "AR" else "💨 High Wind: Be careful!")
    return None

# --- قاموس الكلمات ---
texts = {
    "EN": {
        "title": "Weather Pro Max",
        "search": "Type city name...",
        "temp": "Temperature",
        "wind": "Wind",
        "humidity": "Humidity",
        "hourly": "Next 15 Hours Forecast",
        "shop": "View Amazon Today's Deals 🛒"
    },
    "AR": {
        "title": "وذر برو ماكس",
        "search": "اكتب اسم المدينة...",
        "temp": "الحرارة",
        "wind": "الرياح",
        "humidity": "الرطوبة",
        "hourly": "توقعات الـ 15 ساعة القادمة",
        "shop": "شاهد عروض أمازون اليوم 🛒"
    }
}
T = texts[st.session_state.lang]

# --- دالة جلب البيانات الشاملة (الحالي + التوقعات) ---
@st.cache_data(ttl=600)
def get_full_weather(query):
    try:
        geo = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=1&appid={API_KEY}").json()
        if geo:
            lat, lon, name = geo[0]['lat'], geo[0]['lon'], geo[0]['name']
            curr = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric").json()
            fore = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric").json()
            return curr, fore, name, lat, lon
    except: return None, None, None, None, None
    return None, None, None, None, None

# --- تصميم الواجهة ---
st.markdown(f"<h1 style='text-align:center; color:#0078ff;'>{T['title']}</h1>", unsafe_allow_html=True)

col_lang = st.columns([4, 1, 4])
if col_lang[1].button("🌐 AR/EN"):
    st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
    st.rerun()

query = st.text_input("", placeholder=T["search"], label_visibility="collapsed")

if query:
    curr, fore, name, lat, lon = get_full_weather(query)
    if curr:
        send_telegram_alert(f"📍 بحث جديد: {name}")
        alert = get_alert(curr, st.session_state.lang)
        if alert:
            st.warning(alert)
        st.markdown(f"<h2 style='text-align:center;'>{name}</h2>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric(T["temp"], f"{curr['main']['temp']}°C")
        m2.metric(T["wind"], f"{curr['wind']['speed']} m/s")
        m3.metric(T["humidity"], f"{curr['main']['humidity']}%")
        st.markdown("---")
        st.subheader(T['hourly'])
        cols = st.columns(5)
        for i, item in enumerate(fore['list'][:5]):
            with cols[i]:
                time_hour = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                st.markdown(f"**{time_hour}**")
                st.write(f"{item['main']['temp']}°C")
                st.caption(item['weather'][0]['description'])
        st.markdown("---")
        st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=9)
        st.markdown(f'''
            <div style="background:#ff9900; padding:20px; border-radius:15px; text-align:center; margin-top:20px;">
                <a href="https://www.amazon.eg/s?k=weather&tag={AFFILIATE_ID}" target="_blank" style="color:black; font-weight:bold; text-decoration:none; font-size:20px;">{T["shop"]}</a>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.error("City not found!" if st.session_state.lang == "EN" else "لم يتم العثور على المدينة.")

st.markdown("<br><hr><center>Abdallah Nabil | © 2026 Powered by Amazon Store</center>", unsafe_allow_html=True)
