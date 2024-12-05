import pytest
import requests
from unittest.mock import patch, MagicMock
from models.weather_model import fetch_weather_data, get_current_weather, get_weather_forecast


@patch("models.weather_model.requests.get")
def test_fetch_weather_data_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"temp": 15, "humidity": 80}
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    data = fetch_weather_data("Boston", "weather")
    assert data == {"temp": 15, "humidity": 80}
    mock_get.assert_called_once_with(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"q": "Boston", "appid": "", "units": "metric"},
    )


@patch("models.weather_model.requests.get")
def test_fetch_weather_data_error(mock_get):
    mock_get.side_effect = requests.RequestException("Request Error") 
    with pytest.raises(RuntimeError, match="Error fetching weather data for Boston"):
        fetch_weather_data("Boston", "weather")


@patch("models.weather_model.fetch_weather_data")
def test_get_current_weather(mock_fetch_weather_data):
    mock_fetch_weather_data.return_value = {"temp": 20, "humidity": 70}
    data = get_current_weather("Boston")
    assert data == {"temp": 20, "humidity": 70}
    mock_fetch_weather_data.assert_called_once_with("Boston", "weather")


@patch("models.weather_model.fetch_weather_data")
def test_get_weather_forecast(mock_fetch_weather_data):
    mock_fetch_weather_data.return_value = {"forecast": "Rainy"}
    data = get_weather_forecast("Boston")
    assert data == {"forecast": "Rainy"}
    mock_fetch_weather_data.assert_called_once_with("Boston", "forecast")
