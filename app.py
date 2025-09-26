import streamlit as st
import requests
from groq import Groq

# --------------------------
# API Setup (replace with your key or use env var)
# --------------------------
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# --------------------------
# Weather fetch function
# --------------------------
def fetch_weather(city: str):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    g = requests.get(geo_url, params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=10, verify=False)
    g.raise_for_status()
    gdata = g.json()

    if not gdata.get("results"):
        raise ValueError(f"No location found for {city}")
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
    fore = str(current.get("weathercode", "NA"))

    # Approx humidity
    humidity = None
    if "hourly" in data and "relative_humidity_2m" in data["hourly"]:
        humidity = data["hourly"]["relative_humidity_2m"][0]

    return {
        "temp_c": t,
        "humidity": humidity,
        "forecast": fore
    }

# --------------------------
# Forecast code → label/icon
# --------------------------
def forecast_description(code: str):
    mapping = {
        "0": ("☀️", "Clear sky"),
        "1": ("🌤️", "Mainly clear"),
        "2": ("⛅", "Partly cloudy"),
        "3": ("☁️", "Overcast"),
        "61": ("🌧️", "Rain"),
        "95": ("⛈️", "Thunderstorm"),
        "96": ("⛈️", "Thunderstorm"),
        "99": ("🌩️", "Heavy storm"),
    }
    return mapping.get(code, ("🌍", "Unknown"))

# --------------------------
# Groq LLM for tip
# --------------------------
def get_tip(city, temp, humidity, fore):
    prompt = f"""
    City: {city}, Temperature: {temp}°C, Humidity: {humidity}%, Forecast code: {fore}.
    Provide a single short, practical, energy-saving tip for households in this city based on today's weather.
    Keep it under 25 words.
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()

# --------------------------
# Streamlit UI
# --------------------------
st.set_page_config(page_title="Weather + Energy Tips", page_icon="🌦️", layout="centered")

st.markdown("<h1 style='text-align: center; color:#00ff88;'>🌦️ Smart Weather & Energy Advisor</h1>", unsafe_allow_html=True)

# City dropdown (added Jamnagar)
cities = ["Ahmedabad", "Bengaluru", "Chennai", "Delhi", "Hyderabad", "Jamnagar",
          "Kolkata", "Mumbai", "Pune", "Visakhapatnam"]

city = st.selectbox("Select a city:", cities, index=1)

if st.button("🔍 Get Forecast & Tip"):
    try:
        wx = fetch_weather(city)
        icon, desc = forecast_description(wx["forecast"])

        # Weather Card
        st.markdown(
            f"""
            <div style="background-color:#1b2a21;padding:20px;border-radius:15px;text-align:center;">
                <h2 style="color:#00ff88;">{city}</h2>
                <h1 style="font-size:50px;">{icon}</h1>
                <p style="color:#d1f5d3;font-size:18px;">{desc}</p>
                <p style="color:#d1f5d3;">🌡️ Temp: <b>{wx['temp_c']}°C</b></p>
                <p style="color:#d1f5d3;">💧 Humidity: <b>{wx['humidity']}%</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # LLM Tip
        tip = get_tip(city, wx["temp_c"], wx["humidity"], wx["forecast"])
        st.markdown(
            f"""
            <div style="margin-top:20px;background-color:#0d1117;padding:20px;border-radius:15px;">
                <h3 style="color:#00ff88;">⚡ Energy-Saving Tip</h3>
                <p style="color:#d1f5d3;font-size:16px;">{tip}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.error(f"Error: {e}")
