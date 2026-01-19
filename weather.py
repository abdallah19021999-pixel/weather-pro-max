import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. الإعدادات والجماليات (نفس شكلك الأصلي)
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide")

st.markdown("""
    <style>
    .main { background: linear-gradient(to bottom, #1e3c72, #2a5298); color: white; }
    .stMetric { background: rgba(255, 255, 255, 0.1); padding: 15px; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. المفاتيح السرية
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
AFFILIATE_ID = "abdallah2026-21"

if "lang" not in st.session_state:
    st.session_state.lang = "AR"

# --- القاموس ---
texts = {
    "EN": {"title": "Weather Pro Max", "search": "Search City...", "hourly": "Next Hours Forecast", "shop": "Amazon Deals 🛒"},
    "AR": {"title": "وذر برو ماكس", "search": "ابحث عن مدينة...", "hourly": "توقعات الساعات القادمة", "shop": "عروض أمازون 🛒"}
}
T = texts[st.session_state.lang]

# --- الواجهة ---
st.markdown(f"<h1 style='text-align:center;'>{T['title']}</h1>", unsafe_allow_html=True)

col_lang = st.columns([4, 1, 4])
if col_lang[1].button("🌐 AR/EN"):
    st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
    st.rerun()

query = st.text_input("", placeholder=T["search"], label_visibility="collapsed")

if query:
    try:
        # جلب البيانات
        geo = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=1&appid={API_KEY}").json()
        if geo:
            lat, lon, name = geo[0]['lat'], geo[0]['lon'], geo[0]['name']
            curr = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric").json()
            fore = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric").json()
            
            # --- تنبيه المطر (التحذير) ---
            condition = curr['weather'][0]['main'].lower()
            if "rain" in condition:
                st.warning("⚠️ ستمطر قريباً! خذ مظلتك" if st.session_state.lang == "AR" else "⚠️ Rain expected! Take an umbrella")

            st.markdown(f"<h2 style='text-align:center;'>📍 {name}</h2>", unsafe_allow_html=True)
            
            # العرض الأساسي
            m1, m2, m3 = st.columns(3)
            m1.metric("Temp" if st.session_state.lang=="EN" else "الحرارة", f"{curr['main']['temp']}°C")
            m2.metric("Wind" if st.session_state.lang=="EN" else "الرياح", f"{curr['wind']['speed']} m/s")
            m3.metric("Humidity" if st.session_state.lang=="EN" else "الرطوبة", f"{curr['main']['humidity']}%")

            # --- إضافة توقعات الساعات (بدون تغيير الشكل) ---
            st.markdown(f"### {T['hourly']}")
            f_cols = st.columns(5)
            for i, item in enumerate(fore['list'][:5]):
                with f_cols[i]:
                    time = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                    st.write(f"**{time}**")
                    st.write(f"{item['main']['temp']}°C")

            st.markdown("---")
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=10)
            
            # زر أمازون
            st.markdown(f'''<div style="background:#ff9900; padding:15px; border-radius:10px; text-align:center; margin-top:10px;">
                <a href="https://www.amazon.eg/s?k=weather&tag={AFFILIATE_ID}" target="_blank" style="color:black; font-weight:bold; text-decoration:none;">{T["shop"]}</a>
            </div>''', unsafe_allow_html=True)

            # تنبيه تليجرام
            requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": f"📍 بحث: {name}"})
    except:
        st.error("Error!")

st.markdown("<br><center>Abdallah Nabil © 2026</center>", unsafe_allow_html=True)
