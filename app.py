# weather_groq.py

import requests
import os
from typing import Dict, Any
import streamlit as st
from groq import Groq

# Set API Key
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

def fetch_weather(city: str) -> Dict[str, Any]:
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    g = requests.get(geo_url, params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=10, verify=False)
    g.raise_for_status()
    gdata = g.json()
    if not gdata.get("results"):
        raise ValueError(f"No location found for {city}")
    loc = gdata["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]

    wx_url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon, "current_weather": True,
              "hourly": "temperature_2m,relative_humidity_2m,weathercode"}
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

def get_tip_groq(temp, humidity):
    prompt = f"""
    Current weather:
    - Temperature: {temp} °C
    - Humidity: {humidity} %
    

   Based on the current weather parameter which gives Temperature and humidity. Take the city into consideration as well and, give a **short, practical insight for an user living in india who would use it for their daily usecases like planning their day around the weather forecast to optimize 
   electronic appliances usage and use it to minimize their energy consumption on a daily basis. Keep the tip less than 30 words
    
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  # free model
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

st.title("🌤️ Weather + Energy Tip (Groq Free)")
city = st.selectbox("Select a city:", ["Bengaluru", "Delhi", "Mumbai", "Chennai", "Kolkata", "Hyderabad", "Pune", "Jaipur", "Ahmedabad", "Lucknow"])
if st.button("Get Weather & Tip"):
    wx = fetch_weather(city)
    st.subheader(f"Weather in {city}")
    st.write(f"🌡 Temperature: {wx['temp_c']} °C")
    st.write(f"💧 Humidity: {wx['humidity']} %")
    st.write(f"📡 Forecast code: {wx['forecast']}")
    tip = get_tip_groq(wx['temp_c'], wx['humidity'], wx['forecast'])
    st.subheader("💡 Energy-Saving Tip")
    st.success(tip)



