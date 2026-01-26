import streamlit as st
import requests
import pandas as pd
import random
from datetime import datetime

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Weather Pro Max", 
    page_icon="🌤️", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 2. جلب المفاتيح من الـ Secrets
try:
    API_KEY = st.secrets["OPENWEATHER_API_KEY"]
    TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
    TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except:
    st.error("Missing Secrets Configuration!")
    st.stop()

AFFILIATE_ID = "abdallah2026-21"

# ضبط اللغة الافتراضية للإنجليزية
if "lang" not in st.session_state:
    st.session_state.lang = "EN"

# --- دالة إرسال تنبيه للتليجرام ---
def send_telegram_alert(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, json=payload)
    except: pass

# --- القاموس العربي والإنجليزي ---
texts = {
    "EN": {
        "title": "Weather Pro Max", "search_place": "Type City Name...",
        "btn_analyze": "Explore Analysis & Map", "temp": "Temperature",
        "clouds": "Clouds", "wind": "Wind", "humidity": "Humidity",
        "hourly": "Next Hours Forecast", "shop": "Shop Deals on Amazon 🛒"
    },
    "AR": {
        "title": "وذر برو ماكس", "search_place": "اكتب اسم المدينة...",
        "btn_analyze": "عرض التحليل والخريطة", "temp": "الحرارة",
        "clouds": "الغيوم", "wind": "الرياح", "humidity": "الرطوبة",
        "hourly": "توقعات الساعات القادمة", "shop": "تسوق عروض أمازون 🛒"
    }
}
T = texts[st.session_state.lang]

# --- دالة البحث الذكية (تعطي أولوية لمصر والمدن المحلية) ---
@st.cache_data(ttl=600)
def search_city(query):
    try:
        # المحاولة الأولى: إضافة EG لضمان نتائج مصرية دقيقة (مثل برج العرب أو سيدي جابر)
        search_query = query if "," in query else f"{query}, EG"
        search_url = f"https://api.openweathermap.org/data/2.5/weather?q={search_query}&appid={API_KEY}"
        res = requests.get(search_url).json()
        if res.get("cod") == 200:
            return (res['coord']['lat'], res['coord']['lon'], res['name'])
        
        # المحاولة الثانية: البحث العالمي المفتوح
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=1&appid={API_KEY}"
        geo_res = requests.get(geo_url).json()
        if geo_res:
            return (geo_res[0]['lat'], geo_res[0]['lon'], geo_res[0]['name'])
    except: pass
    return None, None, None

@st.cache_data(ttl=600)
def get_weather_full(lat, lon):
    try:
        curr_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        fore_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        return requests.get(curr_url).json(), requests.get(fore_url).json()
    except: return None, None

# --- واجهة الـ CSS (محسنة بالكامل للـ APK والموبايل) ---
def apply_ui_final(cond, temp):
    cond = cond.lower()
    p_color = "#4facfe" if "rain" in cond else "#ffeb3b" if "clear" in cond else "#94a3b8"
    p_speed = "1s" if "rain" in cond else "10s" if "clear" in cond else "6s"
    particles = "".join([f'<div class="particle" style="left:{random.randint(0, 95)}%; animation-delay:-{random.uniform(0, 10)}s;"></div>' for i in range(20)])
    
    st.markdown(f"""
        <style>
        #MainMenu, footer, header, .stAppDeployButton, #viewerBadge {{visibility: hidden !important; display: none !important;}}
        .stApp {{ background: transparent !important; }}
        
        /* تحسين تجربة الـ APK */
        html, body, [data-testid="stAppViewContainer"] {{
            overflow-x: hidden;
            overscroll-behavior-y: contain;
        }}
        ::-webkit-scrollbar {{ display: none; }}

        .bg {{ position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: radial-gradient(circle at center, #111 0%, #000 100%); z-index: -1; overflow: hidden; }}
        .particle {{ position: absolute; background: {p_color}; width: 1.5px; height: 15px; opacity: 0.3; will-change: transform; animation: fall {p_speed} linear infinite; }}
        @keyframes fall {{ from {{ transform: translateY(-20vh); }} to {{ transform: translateY(110vh); }} }}
        
        .block-container {{padding-top: 1.5rem !important; padding-bottom: 1rem !important;}}
        
        [data-testid="stMetric"] {{ 
            background: rgba(255, 255, 255, 0.05) !important; 
            backdrop-filter: blur(8px); 
            border-radius: 15px !important; 
            padding: 15px !important; 
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .stButton button {{ 
            background: {p_color} !important; 
            color: black !important; 
            font-weight: bold !important; 
            width: 100% !important; 
            border-radius: 12px !important;
            height: 50px !important;
            font-size: 18px !important;
            border: none !important;
        }}

        h1 {{ font-size: 2rem !important; text-align: center !important; color: white !important; margin-bottom: 0.5rem !important; }}
        h2, h3 {{ text-align: center !important; color: white !important; }}
        
        .forecast-box {{ 
            background: rgba(255,255,255,0.03); 
            border-radius: 12px; 
            padding: 12px; 
            text-align: center; 
            border: 1px solid rgba(255,255,255,0.05);
            margin-top: 5px;
        }}

        @media (max-width: 640px) {{
            [data-testid="stMetricValue"] {{ font-size: 1.6rem !important; }}
            .stMarkdown h1 {{ font-size: 1.5rem !important; }}
        }}
        </style>
        <div class="bg">{particles}</div>
        <script>
        if (Notification.permission !== "granted") {{
            Notification.requestPermission();
        }}
        </script>
    """, unsafe_allow_html=True)

# --- التنفيذ الرئيسي ---
st.markdown(f"<h1>{T['title']}</h1>", unsafe_allow_html=True)

c1, c2, c3 = st.columns([1, 0.6, 1])
with c2:
    if st.button("🌐 AR/EN"):
        st.session_state.lang = "AR" if st.session_state.lang == "EN" else "EN"
        st.rerun()

query = st.text_input("", placeholder=T["search_place"], key="search_input", label_visibility="collapsed")
analyze_btn = st.button(T["btn_analyze"])

if query:
    lat, lon, name = search_city(query)
    if lat:
        send_telegram_alert(f"📍 New Search: {name} ({query})")
        curr_data, fore_data = get_weather_full(lat, lon)
        
        if curr_data:
            apply_ui_final(curr_data['weather'][0]['main'], curr_data['main']['temp'])
            
            # --- 🚀 نظام التحذيرات العالمي + إشعارات الدفع 🚀 ---
            cond_main = curr_data['weather'][0]['main'].lower()
            cond_desc = curr_data['weather'][0]['description'].lower()
            temp = curr_data['main']['temp']
            wind = curr_data['wind']['speed']
            vis = curr_data.get('visibility', 10000)
            hum = curr_data['main']['humidity']
            
            alerts = []
            
            # فحص الغبار والأتربة (Dust/Haze/Sand)
            if any(x in cond_main or x in cond_desc for x in ["dust", "sand", "haze", "ash"]):
                alerts.append("🌪️ Dust/Sand Warning! Use a mask" if st.session_state.lang=="EN" else "🌪️ تحذير: عواصف رملية أو أتربة عالقة!")
            
            # الأمطار والرعد
            if "rain" in cond_main or "drizzle" in cond_main:
                alerts.append("⚠️ Rain expected! Umbrella needed" if st.session_state.lang=="EN" else "⚠️ أمطار متوقعة! خذ مظلتك")
            if "thunderstorm" in cond_main:
                alerts.append("⚡ Thunderstorm Warning! Stay safe" if st.session_state.lang=="EN" else "⚡ عاصفة رعدية! ابق في مكان آمن")

            # الرؤية والضباب
            if any(x in cond_main for x in ["fog", "mist", "smoke"]):
                alerts.append("🌫️ Foggy Weather! Drive slowly" if st.session_state.lang=="EN" else "🌫️ ضباب كثيف! انتبه أثناء القيادة")

            # درجات الحرارة والرياح
            if temp > 38:
                alerts.append("🔥 Extreme Heatwave! Stay hydrated" if st.session_state.lang=="EN" else "🔥 موجة حر شديدة! اشرب سوائل")
            elif temp < 7:
                alerts.append("🥶 Freezing Cold! Wear heavy clothes" if st.session_state.lang=="EN" else "🥶 برد قارص! ارتِدِ ملابس ثقيلة")
            
            if wind > 15:
                alerts.append("💨 High Wind Warning!" if st.session_state.lang=="EN" else "💨 رياح عاتية! احذر من التطاير")

            # عرض التنبيهات وإرسال إشعار للموبايل
            for alert in alerts:
                st.warning(alert)
                st.components.v1.html(f"""
                <script>
                if (Notification.permission === "granted") {{
                    new Notification("Weather Alert ⚠️", {{ body: "{alert}", icon: "https://cdn-icons-png.flaticon.com/512/1146/1146860.png" }});
                }}
                </script>
                """, height=0)

            st.markdown(f"<h2>{name}</h2>", unsafe_allow_html=True)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(T["temp"], f"{temp}°C")
            m2.metric(T["clouds"], f"{curr_data['clouds']['all']}%")
            m3.metric(T["wind"], f"{wind} m/s")
            m4.metric(T["humidity"], f"{hum}%")
            
            st.markdown(f"<h3>{T['hourly']}</h3>", unsafe_allow_html=True)
            f_cols = st.columns(5)
            for i, item in enumerate(fore_data['list'][:5]):
                with f_cols[i]:
                    time = datetime.fromtimestamp(item['dt']).strftime('%H:%M')
                    st.markdown(f'<div class="forecast-box"><small style="color:#ccc">{time}</small><br><b style="color:white">{item["main"]["temp"]}°C</b><br><small style="color:#aaa">{item["weather"][0]["main"]}</small></div>', unsafe_allow_html=True)

            if analyze_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=10)
            
            # رابط أمازون
            st.markdown(f'<div style="background:#ff9900; padding:12px; border-radius:12px; text-align:center; margin-top:20px;"><a href="https://www.amazon.eg/s?k=weather&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:black; font-weight:bold;">{T["shop"]}</a></div>', unsafe_allow_html=True)
    else:
        st.error("City not found!")
else:
    apply_ui_final("clear", 25)

st.markdown(f"<p style='text-align:center; opacity:0.3; margin-top:50px; color:white;'>Abdallah Nabil | 2026</p>", unsafe_allow_html=True)
