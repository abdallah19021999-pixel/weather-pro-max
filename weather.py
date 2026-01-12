import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة الأصلية
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

# استدعاء الأسرار
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
AFFILIATE_ID = "abdallah2026-21"

# دالة لجلب البيانات تدعم أي مكان في العالم (عالمي)
@st.cache_data(ttl=600)
def get_weather_data(city_name):
    try:
        # الميزة الذكية: ترجمة أي اسم (مدينة، قرية، إقليم) للإنجليزية لضمان قبول السيرفر
        translated = GoogleTranslator(source='auto', target='en').translate(city_name)
        # البحث باستخدام اسم المدينة المترجم
        url = f"http://api.openweathermap.org/data/2.5/weather?q={translated}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

def load_lottieurl(url: str):
    try: return requests.get(url).json()
    except: return None

def notify_me(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=2)
    except: pass

# --- التنسيق (CSS) الأصلي المحبب لديك ---
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background: linear-gradient(to bottom, #1e3c72, #2a5298); color: white; }}
    
    .ticker-wrap {{
        width: 100%; overflow: hidden; background: rgba(0,0,0,0.3); padding: 8px 0; margin-bottom: 15px;
    }}
    .ticker {{
        display: inline-block; white-space: nowrap; animation: ticker 25s linear infinite; font-weight: bold; color: #00d4ff;
    }}
    @keyframes ticker {{
        0% {{ transform: translateX(100%); }}
        100% {{ transform: translateX(-100%); }}
    }}

    .amazon-ad-box {{
        background: white; color: #232f3e; padding: 20px; border-radius: 15px;
        text-align: center; margin-top: 30px; border-bottom: 5px solid #ff9900;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }}
    .ad-button {{
        background-color: #ff9900; color: white !important; padding: 10px 25px;
        text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block; margin-top: 10px;
    }}

    [data-testid="stMetric"] {{
        background: rgba(255,255,255,0.1); padding: 10px !important; border-radius: 10px; text-align: center;
    }}
    </style>
    """, unsafe_allow_html=True)

# شريط التنبيهات
st.markdown('<div class="ticker-wrap"><div class="ticker">🌍 نظام التتبع العالمي مفعل: يمكنك الآن البحث عن أي مدينة، قرية، أو نجوع في أي مكان بالعالم بالعربي أو الإنجليزي 🌤️</div></div>', unsafe_allow_html=True)

st.title("🌤️ Weather Pro Max Global")

# خانة بحث ذكية مفتوحة (بدون تقييد بمدن معينة)
city_query = st.text_input("📍 اكتب اسم المدينة أو المركز أو القرية (عربي/English):", placeholder="مثال: شبين الكوم، برج العرب، دبي، لندن...")

if city_query:
    weather_data = get_weather_data(city_query)
    
    if weather_data:
        main_cond = weather_data['weather'][0]['main'].lower()
        temp = weather_data['main']['temp']
        city_full_name = weather_data['name'] # الاسم الرسمي من السيرفر
        country_code = weather_data['sys']['country']

        # تحديد الروابط
        if "rain" in main_cond:
            ad_text, p_search = "☔ الدنيا بتمطر؟ الحق عروض الشماسي والملابس المضادة للمطر بخصم خاص!", "umbrella"
        elif temp > 25:
            ad_text, p_search = "🕶️ الجو شمس؟ احمي عينك بأفضل نظارات الشمس الأصلية من أمازون!", "sunglasses"
        elif temp < 15:
            ad_text, p_search = "🧥 الجو برد؟ شوف كولكشن الملابس الشتوية والدفايات الجديد!", "winter+clothes"
        else:
            ad_text, p_search = "🎒 الجو رايق! شوف أحدث عروض شنط الظهر والرحلات المريحة!", "backpacks"

        p_link = f"https://www.amazon.eg/s?k={p_search}&tag={AFFILIATE_ID}"

        # الأنميشن
        anim_urls = {"rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
                     "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
                     "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json",
                     "default": "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"}
        anim_json = load_lottieurl(anim_urls.get(main_cond if main_cond in anim_urls else "default"))
        if anim_json: st_lottie(anim_json, height=220, key="main_anim")

        st.subheader(f"📍 {city_full_name}, {country_code}")

        # عرض المقاييس الـ 4 الأصلية
        c1, c2 = st.columns(2)
        c1.metric("Temperature", f"{temp} °C")
        c2.metric("Clouds", f"{weather_data['clouds']['all']}%")
        
        c3, c4 = st.columns(2)
        c3.metric("Wind Speed", f"{weather_data['wind']['speed']} m/s")
        c4.metric("Humidity", f"{weather_data['main']['humidity']}%")

        if st.button("Explore Local Map & Analysis"):
            notify_me(f"💰 بحث عالمي عن: {city_full_name} | {temp}°C")
            st.map(pd.DataFrame({'lat': [weather_data['coord']['lat']], 'lon': [weather_data['coord']['lon']]}))
            st.image(f"http://openweathermap.org/img/wn/{weather_data['weather'][0]['icon']}@4x.png", width=80)

        # إعلان أمازون
        st.markdown(f"""
            <div class="amazon-ad-box">
                <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="90"><br>
                <p style="margin: 10px 0; font-size: 1.1rem;">{ad_text}</p>
                <a href="{p_link}" target="_blank" class="ad-button">اطلب الآن بخصم خاص 🛒</a>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.error("❌ تعذر العثور على هذا المكان. تأكد من كتابة الاسم بشكل صحيح.")

st.markdown("<br><center style='opacity:0.7;'>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
