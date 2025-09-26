import streamlit as st
import requests
from groq import Groq

# --------------------------
# CONFIG
# --------------------------
API_KEY = "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"  # <-- replace with your Groq key
client = Groq(api_key=API_KEY)

CITIES = [
    "Bengaluru", "Delhi", "Mumbai", "Chennai", "Kolkata",
    "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
]

# --------------------------
# Fetch weather data
# --------------------------
def fetch_weather(city: str):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    g = requests.get(geo_url, params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=10, verify=False)
    g.raise_for_status()
    gdata = g.json()

    if not gdata.get("results"):
        return None

    loc = gdata["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]

    wx_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "temperature_2m,relative_humidity_2m,weathercode"
    }
    r = requests.get(wx_url, params=params, timeout=10, verify=False)
    r.raise_for_status()
    data = r.json()

    current = data.get("current_weather", {})
    t = current.get("temperature")
    fore_code = str(current.get("weathercode", "NA"))

    # weathercode mapping (simplified)
    conditions = {
        "0": "Clear sky ☀️",
        "1": "Mainly clear 🌤",
        "2": "Partly cloudy ⛅",
        "3": "Overcast ☁️",
        "45": "Fog 🌫",
        "48": "Depositing rime fog 🌫",
        "51": "Light drizzle 🌧",
        "61": "Rain 🌧",
        "71": "Snow ❄️",
        "95": "Thunderstorm ⛈",
    }
    fore_text = conditions.get(fore_code, "Unknown")

    humidity = None
    if "hourly" in data and "relative_humidity_2m" in data["hourly"]:
        humidity = data["hourly"]["relative_humidity_2m"][0]

    return {
        "temp_c": t,
        "humidity": humidity,
        "forecast": fore_text
    }

# --------------------------
# Get Energy Saving Tip from Groq LLM
# --------------------------
def get_tip(city, temp, humidity, forecast):
    prompt = f"""
    You are an energy advisor. The user is in {city}.
    Current weather: {temp}°C, {humidity}% humidity, {forecast}.
    Give one crisp, practical energy-saving or safety tip for an Indian household/ indian user who would use this to optimize energy consumption.
    Keep it under 30 words.
    """
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()

# --------------------------
# Streamlit UI
# --------------------------
st.title("🌍 Weather & Energy Advisor")
st.markdown("Get live weather forecast and **smart energy-saving tips** ⚡")

city = st.selectbox("Select a City:", CITIES)

if st.button("Get Forecast"):
    wx = fetch_weather(city)
    if not wx:
        st.error("❌ Could not fetch weather. Try another city.")
    else:
        # Weather Panel
        st.subheader(f"📍 {city} - Today's Weather")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌡 Temperature", f"{wx['temp_c']} °C")
        with col2:
            st.metric("💧 Humidity", f"{wx['humidity']} %")
        with col3:
            st.metric("🌦 Forecast", wx['forecast'])

        # Energy Tip
        st.subheader("💡 Energy-Saving Tip")
        tip = get_tip(city, wx['temp_c'], wx['humidity'], wx['forecast'])
        st.success(tip)

