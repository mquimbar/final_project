import requests
import logging
import os

logger = logging.getLogger(__name__)
API_KEY = os.getenv("WEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5/"

def fetch_weather_data(city: str, endpoint: str) -> dict:
    """
    Fetch weather data from OpenWeather API for a city.

    Args:
        city (str): The city to fetch data for.
        endpoint (str): The endpoint to use ('weather' or 'forecast').

    Returns:
        dict: JSON response from the API.
    """
    url = f"{BASE_URL}{endpoint}"
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        logger.info("Weather data successfully fetched!")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching {endpoint} data for {city}: {e}")
        raise RuntimeError(f"Error fetching {endpoint} data for {city}")

def get_current_weather(city: str) -> dict:
    """
    Get current weather data for a city.
    """
    logger.info("Got current weather!")
    return fetch_weather_data(city, "weather")

def get_weather_forecast(city: str) -> dict:
    """
    Get weather forecast data for a city.
    """
    logger.info("Got weather forecast!")
    return fetch_weather_data(city, "forecast")
