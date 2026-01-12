import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. Page Configuration
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

# --- Search Engine ---
@st.cache_data(ttl=3600)
def get_coordinates(location_name):
    try:
        translated = GoogleTranslator(source='auto', target='en').translate(location_name)
        url = f"https://nominatim.openstreetmap.org/search?q={translated}&format=json&limit=1"
        headers = {'User-Agent': 'WeatherApp_2026'}
        res = requests.get(url, headers=headers, timeout=10).json()
        if res: return float(res[0]['lat']), float(res[0]['lon']), res[0]['display_name']
        return None, None, None
    except: return None, None, None

@st.cache_data(ttl=600)
def get_weather_by_coords(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- Live Weather Visuals ---
def apply_weather_visuals(condition, temp):
    bg_gradient = "linear-gradient(to bottom, #1e3c72, #2a5298)"
    overlay = ""
    
    if "rain" in condition or "drizzle" in condition:
        bg_gradient = "linear-gradient(to bottom, #203a43, #2c5364)"
        overlay = '<div style="position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:0; pointer-events:none; background: url(\'https://raw.githubusercontent.com/fomantic/Fomantic-UI/master/test/visual/assets/images/rain.png\'); opacity: 0.2; animation: rain_m 0.5s linear infinite;"></div><style>@keyframes rain_m { from {background-position: 0 0;} to {background-position: 40px 400px;} }</style>'
    elif "clear" in condition or temp > 28:
        bg_gradient = "linear-gradient(135deg, #FF8C00 0%, #FFD700 100%)"
        overlay = '<div style="position:fixed; top:-100px; right:-100px; width:450px; height:450px; background:radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%); z-index:0; pointer-events:none;"></div>'
    elif "snow" in condition:
        bg_gradient = "linear-gradient(to bottom, #83a4d4, #b6fbff)"
        overlay = '<div style="position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:0; pointer-events:none; background: url(\'https://www.transparenttextures.com/patterns/snow.png\'); opacity: 0.6;"></div>'

    st.markdown(f"""
        <style>
        .stApp {{ background: {bg_gradient}; transition: all 1s ease; color: white; }}
        [data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(5px); border-radius: 12px; }}
        .main-card {{ background: rgba(0, 0, 0, 0.3); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); margin-top: 15px; }}
        .amazon-footer {{ background: white; color: #232f3e; padding: 15px; border-radius: 15px; text-align: center; margin-top: 50px; border-bottom: 5px solid #ff9900; max-width: 500px; margin-left: auto; margin-right: auto; }}
        </style>
        {overlay}
        """, unsafe_allow_html=True)

# --- App Layout ---
st.markdown("<h1 style='text-align: center;'>🌤️ Weather Pro Max</h1>", unsafe_allow_html=True)

search_city = st.text_input("📍 Search City (English/عربي):", placeholder="Enter location name...")

# We use session state to track if details should be shown
if "show_details" not in st.session_state:
    st.session_state.show_details = False

if search_city:
    lat, lon, display_name = get_coordinates(search_city)
    
    if lat:
        data = get_weather_by_coords(lat, lon)
        if data:
            cond = data['weather'][0]['main'].lower()
            temp = data['main']['temp']
            apply_weather_visuals(cond, temp)

            # Weather Animation
            anim_urls = {
                "rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
                "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
                "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json"
            }
            anim_json = load_lottieurl(anim_urls.get(cond, "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"))
            if anim_json: st_lottie(anim_json, height=180, key="weather_anim")

            st.markdown(f"<h3 style='text-align:center;'>{display_name}</h3>", unsafe_allow_html=True)
            
            # --- Constant Button Location ---
            col_btn1, col_btn2, col_btn3 = st.columns([1,1,1])
            with col_btn2:
                show_btn = st.button("Explore Local Map & Analysis", use_container_width=True)
            
            if show_btn:
                st.session_state.show_details = not st.session_state.show_details

            if st.session_state.show_details:
                st.markdown("<div class='main-card'>", unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Temperature", f"{temp}°C")
                m2.metric("Clouds", f"{data['clouds']['all']}%")
                m3.metric("Wind Speed", f"{data['wind']['speed']} m/s")
                m4.metric("Humidity", f"{data['main']['humidity']}%")
                st.markdown("---")
                st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=11)
                st.markdown("</div>", unsafe_allow_html=True)

            # Smart Recommendations
            p_cat = "umbrella" if "rain" in cond else "sunglasses" if temp > 28 else "winter+jacket"
            rec_msg = "Stay safe and check our top picks for today's weather!"

            # Footer
            st.markdown(f"<center style='color:white; opacity:0.6; margin-top:60px;'>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="amazon-footer">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="70"><br>
                    <p style="margin:5px 0;"><b>Recommendation:</b> {rec_msg}</p>
                    <a href="https://www.amazon.eg/s?k={p_cat}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold;">Shop on Amazon 🛒</a>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("Location not found.")
else:
    st.markdown("<style>.stApp { background: linear-gradient(to bottom, #1e3c72, #2a5298); }</style>", unsafe_allow_html=True)
