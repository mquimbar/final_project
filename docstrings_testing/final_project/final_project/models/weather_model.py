import requests
import logging
import os
from final_project.db import db
from final_project.utils.logger import configure_logger
from final_project.clients.redis_client import redis_client
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from dataclasses import asdict, dataclass
from typing import Any, List


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

class WeatherModel:
    # __tablename__ = 'weather'

    # id: int = db.Column(db.Integer, primary_key=True)
    # meal: str = db.Column(db.String(80), unique=True, nullable=False)
    # cuisine: str = db.Column(db.String(50))
    # price: float = db.Column(db.Float, nullable=False)
    # difficulty: str = db.Column(db.String(10), nullable=False)
    # battles: int = db.Column(db.Integer, default=0)
    # wins: int = db.Column(db.Integer, default=0)
    # deleted: bool = db.Column(db.Boolean, default=False)

    # def __init__(self):
    #     """Initializes the BattleManager with an empty list of combatants and TTL."""
    #     self.city: str  # List of active combatants

    def get_current_weather(city: str) -> dict:
        """
        Get current weather data for a city.
        """
        logger.info("Got current weather!")
        return fetch_weather_data(city, "weather")

    def get_weather_forecast(city: str) -> dict:
        """
        Get weather forecast data for a city, forecast.
        """
        logger.info("Got weather forecast!")
        return fetch_weather_data(city, "forecast")
    
    def get_current_visibility(city: str) -> dict:
        """
        Get current weather data for a city, visibility.
        """
        logger.info("Got current visibility!")
        return fetch_weather_data(city, "visibility")
    
    def get_current_clouds(city: str) -> dict:
        """
        Get current weather data for a city, clouds.
        """
        logger.info("Got current clouds!")
        return fetch_weather_data(city, "clouds")
    
    def get_current_wind(city: str) -> dict:
        """
        Get current weather data for a city, wind.
        """
        logger.info("Got current wind!")
        return fetch_weather_data(city, "wind")
