import streamlit as st
import requests
import pandas as pd
from streamlit_lottie import st_lottie
from deep_translator import GoogleTranslator

# 1. Page Config
st.set_page_config(page_title="Weather Pro Max", page_icon="🌤️", layout="wide", initial_sidebar_state="collapsed")

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
AFFILIATE_ID = "abdallah2026-21"

# --- Search Engine (OSM for High Accuracy) ---
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
        return requests.get(url, timeout=5).json()
    except: return None

def load_lottieurl(url: str):
    try: return requests.get(url).json()
    except: return None

# --- Dynamic Weather Visuals (CSS & Backgrounds) ---
def apply_weather_visuals(condition, temp):
    # Default Visuals
    bg_gradient = "linear-gradient(to bottom, #1e3c72, #2a5298)"
    overlay = ""
    
    if "rain" in condition or "drizzle" in condition:
        bg_gradient = "linear-gradient(to bottom, #203a43, #2c5364)"
        # Rain Animation Overlay
        overlay = """
        <div style="position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:0; pointer-events:none; 
        background: url('https://raw.githubusercontent.com/fomantic/Fomantic-UI/master/test/visual/assets/images/rain.png'); 
        opacity: 0.3; animation: rain_move 0.5s linear infinite;"></div>
        <style>@keyframes rain_move { from {background-position: 0 0;} to {background-position: 50px 500px;} }</style>
        """
    elif "snow" in condition:
        bg_gradient = "linear-gradient(to bottom, #83a4d4, #b6fbff)"
        overlay = '<div style="position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:0; pointer-events:none; background: url(\'https://www.transparenttextures.com/patterns/snow.png\'); opacity: 0.8;"></div>'
    elif "clear" in condition or temp > 28:
        bg_gradient = "linear-gradient(135deg, #FF8C00 0%, #FFD700 100%)"
        # Sun Glow Effect
        overlay = '<div style="position:fixed; top:-150px; right:-150px; width:500px; height:500px; background:radial-gradient(circle, rgba(255,255,255,0.4) 0%, transparent 70%); z-index:0; pointer-events:none;"></div>'

    st.markdown(f"""
        <style>
        .stApp {{ background: {bg_gradient}; transition: all 1s ease; }}
        [data-testid="stMetric"] {{ background: rgba(255, 255, 255, 0.1) !important; backdrop-filter: blur(5px); border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); }}
        .main-card {{ background: rgba(0, 0, 0, 0.2); padding: 25px; border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); }}
        .amazon-footer {{ background: white; color: #232f3e; padding: 15px; border-radius: 15px; text-align: center; margin-top: 20px; border-bottom: 5px solid #ff9900; max-width: 500px; margin-left: auto; margin-right: auto; }}
        </style>
        {overlay}
        """, unsafe_allow_html=True)

# --- UI Layout ---
st.markdown("<h1 style='text-align: center; color: white;'>🌤️ Weather Pro Max</h1>", unsafe_allow_html=True)

search_city = st.text_input("📍 Search City, Village or Province (English/عربي):", placeholder="e.g. Borg El Arab, Alexandria...")

if search_city:
    lat, lon, display_name = get_coordinates(search_city)
    
    if lat:
        data = get_weather_by_coords(lat, lon)
        if data:
            cond = data['weather'][0]['main'].lower()
            temp = data['main']['temp']
            
            apply_weather_visuals(cond, temp)

            # 1. Main Weather Animation
            anim_urls = {
                "rain": "https://lottie.host/9331e84a-c0b9-4f7d-815d-ed0f48866380/vGvFjPqXWp.json",
                "clear": "https://lottie.host/a8a5b293-61a7-47b8-80f2-b892a4066c0d/Y08T7N1p5N.json",
                "clouds": "https://lottie.host/17e23118-2e0f-48e0-a435-081831412d2b/qQ0JmX24jC.json"
            }
            anim_json = load_lottieurl(anim_urls.get(cond, "https://lottie.host/a06d87f7-f823-4556-9a5d-b4b609c2a265/gQz099j54N.json"))
            st_lottie(anim_json, height=200)

            # 2. Location & Stats
            st.markdown(f"<h3 style='text-align:center; color:white;'>{display_name}</h3>", unsafe_allow_html=True)
            
            st.markdown("<div class='main-card'>", unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Temperature", f"{temp} °C")
            m2.metric("Clouds", f"{data['clouds']['all']}%")
            m3.metric("Wind", f"{data['wind']['speed']} m/s")
            m4.metric("Humidity", f"{data['main']['humidity']}%")
            
            # 3. The Map
            st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}), zoom=11)
            st.markdown("</div>", unsafe_allow_html=True)

            # 4. Amazon Recommendations Logic
            if "rain" in cond:
                rec, p_url = "Rainy Day! Get an Umbrella or Waterproof Jacket ☔", "waterproof+jacket+umbrella"
            elif temp > 28:
                rec, p_url = "Sunny Day! Perfect for Sunglasses & Sunscreen 🕶️", "sunglasses+sunscreen"
            elif temp < 15:
                rec, p_url = "Cold Weather! Stay warm with Jackets & Boots 🧥", "winter+clothes+boots"
            else:
                rec, p_url = "Great Weather! Check our latest Backpacks & Sneakers 👟", "backpack+sneakers"

            # Footer
            st.markdown(f"<center style='color:white; opacity:0.6; margin-top:30px;'>Created by: Abdallah Nabil | 2026</center>", unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="amazon-footer">
                    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg" width="80"><br>
                    <p style="margin:5px 0;"><b>Our Recommendation:</b> {rec}</p>
                    <a href="https://www.amazon.eg/s?k={p_url}&tag={AFFILIATE_ID}" target="_blank" style="text-decoration:none; color:#0066c0; font-weight:bold;">Shop the look on Amazon 🛒</a>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.error("City not found. Please try adding the province name.")
else:
    # Default Theme
    st.markdown("<style>.stApp { background: linear-gradient(to bottom, #1e3c72, #2a5298); }</style>", unsafe_allow_html=True)
