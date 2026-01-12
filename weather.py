import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. إعدادات الصفحة - حافظنا على الـ Layout الأصلي
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

# استدعاء الأسرار
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
AFFILIATE_ID = "abdallah2026-21"

# قائمة الاقتراحات اللي طلبتها (بتظهر وأنت بتكتب)
SUGGESTED_CITIES = ["Cairo", "Alexandria", "Giza", "Aswan", "Luxor", "Sharm El Sheikh", "Hurghada", "Mansoura", "Tanta", "Dubai", "London", "Paris"]

# تحسين السرعة باستخدام الـ Caching
@st.cache_data(ttl=600)
def get_weather_data(city_name):
    try:
        # ميزة البحث بالعربي: الترجمة التلقائية
        translated = GoogleTranslator(source='auto', target='en').translate(city_name)
        url = f"http://api.openweathermap.org/data/2.5/weather?q={translated}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=5) # قللت الـ timeout لزيادة السرعة
        return r.json() if r.status_code == 200 else None
    except: return None

def load_lottieurl(url: str):
    try: return requests.get(url).json()
    except: return None

def notify_me(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg}, timeout=2)
    except: pass

# --- الـ CSS الأصلي (الخلفية الزرقاء والشريط وكل شيء كما هو) ---
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

# 1. الشريط المتحرك (Ticker) - موجود
st.markdown('<div class="ticker-wrap"><div class="ticker">🚀 تحديثات 2026: دعم البحث باللغة العربية | ميزة الاقتراحات الذكية مفعلة | تسوق الآن حسب حالة الطقس 🌤️</div></div>', unsafe_allow_html=True)

st.title("🌤️ Weather Pro Max Dashboard")

# 2. ميزة البحث بالعربي والاقتراحات (Autocomplete)
city_input = st.selectbox("Search or Select City (Arabic/English):", options=SUGGESTED_CITIES, index=1)
custom_city = st.text_input("Or Type Any City Name:")

final_city = custom_city if custom_city else city_input

weather_data = get_weather_data(final_city)

if weather_data:
    main_cond = weather_data['weather'][0]['main'].lower()
    temp = weather_data['main']['temp']
    
    # تحديد روابط أمازون - موجودة
    if "rain" in main_cond:
        ad_text = "☔ الدنيا بتمطر؟ الحق عروض الشماسي والملابس المضادة للمطر بخصم خاص!"
        p_link = f"https://www.amazon.eg/s?k=umbrella&tag={AFFILIATE_ID}"
    elif temp > 25:
        ad_text = "🕶️ الجو شمس؟ احمي عينك بأفضل نظارات الشمس الأصلية من أمازون!"
        p_link = f"https://www.amazon.eg/s?k=sunglasses&tag={AFFILIATE_ID}"
    elif temp < 15:
        ad_text = "🧥 الجو برد؟ شوف كولكشن الملابس الشتوية والدفايات الجديد!"
        p_link = f"https://www.amazon.eg/s?k=winter+clothes&tag={AFFILIATE_ID}"
    else:
        ad_text = "🎒 الجو رايق! شوف أحدث عروض شنط الظهر والرحلات المريحة!"
        p_link = f"https://www.amazon.eg/s?k=backpacks&tag={AFFILIATE_ID}"

    # الأنميشن - موجود
    anim_urls = {"rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
                 "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
                 "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json",
                 "default": "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"}
    
    anim_json = load_lottieurl(anim_urls.get(main_cond if main_cond in anim_urls else "default"))
    if anim_json: st_lottie(anim_json, height=250, key="main_anim")

    # زر التقرير والبيانات (الـ 4 مقاييس والخريطة) - موجودة بالكامل
    if st.button("Analysis Details"):
        notify_me(f"💰 بحث عن {final_city} | {temp}°C")
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        c1.metric("Temperature", f"{temp} °C")
        c2.metric("Rain/Clouds", f"{weather_data['clouds']['all']}%")
        
        c3, c4 = st.columns(2)
        c3.metric("Wind Speed", f"{weather_data['wind']['speed']} m/s")
        c4.metric("Humidity", f"{weather_data['main']['humidity']}%")
        
        st.markdown("---")
        st.map(pd.DataFrame({'lat': [weather_data['coord']['lat']], 'lon': [weather_data['coord']['lon']]}))
        
        icon_code = weather_data['weather'][0]['icon']
        st.image(f"http://openweathermap.org/img/wn/{icon_code}@4x.png", width=80)

    # إعلان أمازون الذكي - موجود
    st.markdown(f"""
        <div class="amazon-ad-box">
            <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="90"><br>
            <p style="margin: 10px 0; font-size: 1.1rem;">{ad_text}</p>
            <a href="{p_link}" target="_blank" class="ad-button">اطلب الآن بخصم خاص 🛒</a>
        </div>
    """, unsafe_allow_html=True)

else:
    st.warning("Please enter a valid city name.")

st.markdown("<br><center style='opacity:0.7;'>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
