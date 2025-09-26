import streamlit as st
import requests
from groq import Groq

# --------------------------
# API Setup
# --------------------------
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# --------------------------
# Weather fetch function
# --------------------------
def fetch_weather(city: str):
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    g = requests.get(
        geo_url,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10,
        verify=False,
    )
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
        "hourly": "temperature_2m,relative_humidity_2m,weathercode",
    }
    r = requests.get(wx_url, params=params, timeout=10, verify=False)
    r.raise_for_status()
    data = r.json()

    current = data.get("current_weather", {})
    t = current.get("temperature")
    fore = str(current.get("weathercode", "NA"))

    humidity = None
    if "hourly" in data and "relative_humidity_2m" in data["hourly"]:
        humidity = data["hourly"]["relative_humidity_2m"][0]

    return {"temp_c": t, "humidity": humidity, "forecast": fore}

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
        model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# --------------------------
# Streamlit UI
# --------------------------
st.set_page_config(page_title="Weather + Energy Tips", page_icon="🌦️", layout="centered")

st.markdown(
    """
    <style>
        body {
            background-color: #0B0F19;
            color: #E6EDF3;
        }
        .stButton>button {
            background-color: #00C2A8;
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 0.6em 1.2em;
        }
        .stSelectbox label {
            color: #E6EDF3 !important;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='text-align: center; color:#00C2A8;'>🌦️ Smart Weather & Energy Advisor</h1>",
    unsafe_allow_html=True,
)

# City dropdown (added Jamnagar)
cities = [
    "Ahmedabad",
    "Bengaluru",
    "Chennai",
    "Delhi",
    "Hyderabad",
    "Jamnagar",
    "Kolkata",
    "Mumbai",
    "Pune",
    "Visakhapatnam",
]

city = st.selectbox("Select a city:", cities, index=1)

if st.button("🔍 Get Forecast & Tip"):
    try:
        wx = fetch_weather(city)
        icon, desc = forecast_description(wx["forecast"])

        # Weather Card
        st.markdown(
            f"""
            <div style="background-color:#1B1F2A;padding:25px;border-radius:20px;text-align:center;box-shadow:0px 4px 12px rgba(0,0,0,0.5);">
                <h2 style="color:#00C2A8; margin-bottom:10px;">{city}</h2>
                <div style="font-size:60px;">{icon}</div>
                <p style="color:#E6EDF3;font-size:18px;margin:5px;">{desc}</p>
                <p style="color:#E6EDF3;margin:5px;">🌡️ <b>{wx['temp_c']}°C</b></p>
                <p style="color:#E6EDF3;margin:5px;">💧 <b>{wx['humidity']}%</b></p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # LLM Tip Card
        tip = get_tip(city, wx["temp_c"], wx["humidity"], wx["forecast"])
        st.markdown(
            f"""
            <div style="margin-top:20px;background-color:#0E1117;padding:20px;border-radius:15px;box-shadow:0px 4px 12px rgba(0,0,0,0.5);">
                <h3 style="color:#00C2A8;">⚡ Energy-Saving Tip</h3>
                <p style="color:#E6EDF3;font-size:16px;">{tip}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.error(f"Error: {e}")
