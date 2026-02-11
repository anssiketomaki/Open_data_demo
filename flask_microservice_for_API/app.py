from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import requests

app = Flask(__name__)

# Load environment variables
load_dotenv()

# OpenWeatherMap API base URL and key (replace 'YOUR_API_KEY' with your actual key)
LOCATION_API_BASE_URL = "https://api.openweathermap.org/geo/1.0/direct"
WEATHER_API_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = os.getenv("OPENWEATHER_API_KEY")

@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Endpoint to fetch weather information for a given city.
    Query Parameter: city (str) - The city name.
    """
    city = request.args.get('city')
    
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    try:
        # Construct the request to OpenWeatherMap geocoding API to get the city's latitude and longitude
        loc_params = {
            'q': city,
            'limit': 1,
            'appid': API_KEY,
        }
        response = requests.get(LOCATION_API_BASE_URL, params=loc_params)

        if response.status_code == 200:
            data = response.json()
            if not data:
                return jsonify({"error": "City not found"}), 404
            lat = data[0]["lat"]
            lon = data[0]["lon"]
        else:
            return jsonify({"error": "City not found or other error", "details": response.json()}), response.status_code
        
        # Construct the request to OpenWeatherMap weather API to get the weather information
        params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': 'metric'  # Fetch temperature in Celsius
        }
        response = requests.get(WEATHER_API_BASE_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            # Extract relevant fields
            weather_info = {
                "city": city,
                "weather_station": data.get("name"),
                "temperature": data["main"]["temp"],
                "units": "metric",
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"]
            }
            return jsonify(weather_info), 200
        else:
            return jsonify({"error": "Weather data not found or other error", "details": response.json()}), response.status_code

    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
