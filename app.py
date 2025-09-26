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
    Based on the weather information, give some energy tips to the user like the ones i have mentioned below. These are only examples. In the output display just the tip and nothing else. Keep it crisp(under 40 words) and if suggestions, give 4 or less suggestions, dont display the text "Type" in the output
 
    Type - 1: Sunny 36°C, 40% humidity
    Energy &safety tips:Use ceiling fans before switching on AC. Keep curtains/blinds closed in the afternoon to reduce room heating. Prefer using coolers instead of AC when possible. Try to use washing machine/iron during morning-afternoon hours and try not to dry clothes on dryer but use sunlight instead. Safety: Stay hydrated and avoid overloading power strips.
 
    type-2:Hot & Humid, 33°C, 75% humidity
    Energy & safety tips: Run ceiling fans at full speed instead of AC for mild relief. If AC is required, set it at 25–27°C for efficiency. Use natural ventilation for light in the day time. Dry clothes outside when possible instead of using dryers. Safety: Prevent mold by keeping bathrooms and kitchens ventilated.
 
    type - 3:Pleasant Cloudy Evening, 24°C, 65% humidity
    Energy and safety tips: Avoid unnecessary lighting — daylight is sufficient. Switch off fans when not required. Charge inverter/UPS when power is stable. Safety: Protect balconies/wires in case of sudden drizzle.
 
    type -4:Rainy, 26°C, 85% humidity  
    Energy & safety tips:Reduce use of geysers — water is naturally warmer. Unplug appliances during lightning storms. Use inverter backup wisely — only for essentials. Avoid outdoor decorative lights. Safety: Do not touch electrical equipment with wet hands.
 
    type -5:Cloudy, 29°C, 60% humidity
    Energy & safety tips:Switch off unnecessary lights; use natural daylight. Avoid running fans in unused rooms. Delay using washing machines until off-peak hours. Safety: Check plug points near kitchens/bathrooms for leakage currents.
 
    type -6: Winter Cold, 12°C, 55% humidity
    Energy & safety tips:   Use woolen blankets and warm clothing before turning on room heaters. Run geysers for shorter durations. Avoid using immersion rods/coil heaters unless necessary. Safety: Do not leave room heaters on overnight; ventilate rooms with gas heaters.
 
    type -7:  Foggy Morning, 9°C, 65% humidity
    Energy & safety tips:   Open windows after sunrise for natural heating. Avoid overusing heaters; layer clothing instead. Switch outdoor CFL/tube lights to LEDs. Safety: Ensure ventilation when using gas stoves/heaters.
 
    type -8:Heatwave, 42°C, 30% humidity
    Energy & safety tips:Avoid running AC all day — use desert coolers. Cook in mornings/evenings to avoid adding heat indoors. Keep fridge doors closed as much as possible. Cover rooftop water tanks. Safety: Avoid direct sunlight exposure; check inverters during power cuts.
 
    type -9: Overcast, 31°C, 70% humidity
    Energy & safety tips:   Run fans and keep windows closed. Avoid switching on lights during daytime. Use washing machines in afternoon if you have solar panels. Safety: Ensure proper earthing to avoid dampness damage.
 
    type -10: Dust Storm, 37°C, 40% humidit
    Energy & safety tips: y Keep windows/doors shut to reduce dust entry. Clean AC/cooler filters frequently. Switch off unnecessary appliances to avoid damage from flickering supply. Safety: Unplug sensitive devices during storms.
 
    type -11: Pleasant Evening, 25°C, 50% humidity
    Energy & safety tips:Turn off AC completely — rely on natural ventilation. Use minimal lighting — LEDs only when needed. Charge inverter and devices at late night or afternoons during off-peak tariff. Safety: Use mosquito protection methods.
 
    type -12: Drizzle, 27°C, 80% humidity
    Energy & safety tips:   Keep windows slightly open for airflow, avoid AC. Dry clothes under shade with airflow. Use inverter power only for essentials. Safety: Avoid touching outdoor wires. And charge all your devices inprior as there may be a power cut. leave 10 min early to avoid wasting fuel in traffic.
 
    type -13:  Scorching Afternoon, 39°C, 35% humidity
    Energy & safety tips:   Run ceiling fans with AC for better circulation. Switch off unnecessary appliances during peak heat hours. Use pressure cookers for cooking. Safety: Use stabilizers for AC/fridge during voltage fluctuations.
 
    type -14: Chilly weather, 8°C, 40% humidity
    Energy & safety tips:   Use heavy blankets instead of heaters while sleeping. Heat water in bulk and store in flasks. Seal windows with curtains. Safety: Switch off electric blankets/heaters when unattended.
 
    type -15: High Humidity, 32°C, 90% humidity
    Energy & safety tips:   Use ceiling fans at high speed; avoid AC unless necessary and if needed turn on along with fan. Use exhaust fans to reduce dampness. Minimize fridge door openings. Safety: Ensure wiring is insulated against moisture.
 
    type -16: Light Breeze, 26°C, 55% humidity
    Energy & safety tips:   Open windows for cross-ventilation instead of fans. Avoid AC at night. Switch off balcony/tube lights when not needed. Safety: Use mosquito nets/repellents in coastal regions.
 
    type -17:Cold & Rainy, 16°C, 70% humidity
    Energy & safety tips:   Minimize geyser use — heat once and store. Use woolens before heaters. Avoid drying clothes indoors without ventilation. Safety: Keep wiring dry near balconies/windows.And charge all your devices inprior as there may be a power cut. leave 10 min early to avoid wasting fuel in traffic .
 
    type -18: Mild Winter Afternoon, 20°C, 50% humidity
    Energy & safety tips:   No need for heaters/AC — open windows for airflow. Run washing machines in daytime. Use sunlight for disinfecting clothes and bedding. Safety: Ensure LPG stoves are properly shut.
 
    type -19: Stormy Weather, 28°C, 70% humidity
    Energy & safety tips:   Unplug appliances to avoid surge damage. Limit inverter use to essentials. Avoid running electric water pumps. Safety: Stay indoors, avoid stepping out near electric poles.And charge all your devices inprior as there may be a power cut. leave 10 min early to avoid wasting fuel in traffic.
 
    type 20:  Dry Winter Morning, 14°C, 30% humidity
    Energy & safety tips:   Use sunlight for warmth. Switch off geyser immediately after heating water. Prefer warm clothing over heaters. Safety: Keep heaters away from curtains and flammable materials.
   
    """
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant", messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
 
# --------------------------
# Streamlit UI
# --------------------------
st.set_page_config(page_title="ENERSAVE", page_icon="🌦️", layout="centered")
 
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
    "<h1 style='text-align: center; color:#00C2A8;'>🌦️ Your Energy Your Way</h1>",
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
 
if st.button("🔍 Get Insights"):
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
<h3 style="color:#00C2A8;">⚡ Energy Insights</h3>
<p style="color:#E6EDF3;font-size:16px;">{tip}</p>
</div>
            """,
            unsafe_allow_html=True,
        )
 
    except Exception as e:
        st.error(f"Error: {e}")








