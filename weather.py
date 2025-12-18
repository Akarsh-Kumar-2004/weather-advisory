import streamlit as st
import requests
import os
from huggingface_hub import InferenceClient

# Set your API keys
OPENWEATHER_API_KEY = "e370bc4c82f808e76c575b8899e3540f"
HF_TOKEN = "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"
os.environ["HUGGINGFACEHUB_API_TOKEN"] = HF_TOKEN

# Initialize Hugging Face Inference Client
client = InferenceClient(
    model="HuggingFaceH4/zephyr-7b-beta",
    token=HF_TOKEN
)

# Weather condition-based backgrounds
WEATHER_BACKGROUNDS = {
    "clear": "#FFD700",  # Sunny - Gold
    "clouds": "#A9A9A9",  # Cloudy - Dark Gray
    "rain": "#4682B4",  # Rainy - Steel Blue
    "thunderstorm": "#4B0082",  # Thunderstorm - Indigo
    "snow": "#ADD8E6",  # Snow - Light Blue
    "mist": "#D3D3D3",  # Mist - Light Gray
    "default": "#FFFFFF"  # Default - White
}

# Weather condition-based emojis/icons
WEATHER_ICONS = {
    "clear": "☀️",
    "clouds": "☁️",
    "rain": "🌧️",
    "thunderstorm": "⛈️",
    "snow": "❄️",
    "mist": "🌫️",
    "default": "❓"
}

# Function to get weather data
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?appid={OPENWEATHER_API_KEY}&q={city}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_condition = data['weather'][0]['main'].lower()
        description = data['weather'][0]['description'].capitalize()
        temperature = round(data['main']['temp'])
        humidity = data['main']['humidity']
        return weather_condition, description, temperature, humidity
    else:
        return None

# Function to generate a weather summary using HF InferenceClient
def generate_weather_summary(city, description, temperature, humidity):
    prompt = f"The weather in {city} is currently {description} with a temperature of {temperature}°C and humidity at {humidity}%. Provide a short summary and advisory for people."
    result = client.text_generation(prompt=prompt, max_new_tokens=100, temperature=0.6)
    return result.strip()

# Streamlit UI
st.set_page_config(page_title="City Weather Check", page_icon="🌤️", layout="centered")
st.sidebar.header("Enter City Name")
city = st.sidebar.text_input("City", placeholder="Enter city name...")

if city:
    if st.button("Check Weather"):
        with st.spinner("Fetching weather data..."):
            weather = get_weather(city)
            if weather:
                condition, description, temperature, humidity = weather
                summary = generate_weather_summary(city, description, temperature, humidity)

                background_color = WEATHER_BACKGROUNDS.get(condition, WEATHER_BACKGROUNDS["default"])
                weather_icon = WEATHER_ICONS.get(condition, WEATHER_ICONS["default"])

                # Apply custom background color
                st.markdown(f"""
                    <style>
                        .main {{
                            background-color: {background_color};
                            padding: 20px;
                            border-radius: 10px;
                        }}
                        .weather-box {{
                            text-align: center;
                            padding: 20px;
                            border-radius: 10px;
                            background-color: white;
                            width: 300px;
                            margin: auto;
                        }}
                        .temperature {{
                            font-size: 50px;
                            font-weight: bold;
                        }}
                        .icon {{
                            font-size: 80px;
                        }}
                    </style>
                    <div class="main">
                        <div class="weather-box">
                            <div class="icon">{weather_icon}</div>
                            <p class="temperature">{temperature}°C</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                st.subheader(f"Weather in {city}")
                st.write(f"**Condition:** {description}")
                st.write(f"**Humidity:** {humidity}%")

                st.markdown("### AI Generated Summary")
                st.write(summary)
            else:
                st.error("City not found. Please enter a valid city name.")
