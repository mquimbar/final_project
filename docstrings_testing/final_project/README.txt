Weather Dashboard Application

Overview:
The Weather Dashboard is a web-based application designed to provide users with easy access to weather information. 
This application allows users to set favorite locations and quickly view current, forecasted, and historical weather data for these locations. 
By offering userspecific customization, the Weather Dashboard aims to deliver a personalized weather tracking experience, 
making it easier for users to get the most relevant weather information based on their interests and needs. 

Features & Routes:

1. Route: /add-favorite-city
   Request Type: POST
   Purpose: Allows users to save a location as a favorite.
   Request Body: location (String): Name of the city or area to be added to favorites.
   Response Format: JSON
        Success Response Example: "City successfully added to the database: New York"
        
   Example Request: add_favorite_city("New York")

   Example Response: "City successfully added to the database: New York"

2. Route: /get-favorite-cities
   Request Type: GET
   Purpose: Retrieves the list of all saved favorite locations along with their current weather data.
   Response Format: JSON
       Success Response Example: "City retrieved from cache: New York"
       
   Example Request: get_favorite_cities()
    
   Example Response: "City retrieved from cache: New York"

3. Route: /delete-favorite-city
   Request Type: DELETE
   Purpose: deletes the favorite city that the user specifies.
   Response Format: JSON
       Success Response Example: "City with id 1 marked as deleted."
       
   Example Request: delete_favorite_city("New York")
    
   Example Response: "City with id 1 marked as deleted."

4. Route: /get-current-weather
   Request Type: GET
   Purpose: Fetches the current weather details for a saved favorite location.
   Response Format: JSON
       Success Response Example: 
      "weather": [
         {
            "id": 501,
            "main": "Rain",
            "description": "moderate rain",
            "icon": "10d"
         }
      ]
       
   Example Request: get_current_weather("New York")
    
   Example Response:
   "weather": [
      {
         "id": 501,
         "main": "Rain",
         "description": "moderate rain",
         "icon": "10d"
      }
   ]

5. Route: /get-weather-forecast
   Request Type: GET
   Purpose: Retrieves forecast weather data for a user's favorite location.
   Response Format: JSON
       Success Response Example: would display weather, as seen below, for next day
      "weather": [
         {
            "id": 501,
            "main": "Rain",
            "description": "moderate rain",
            "icon": "10d"
         }
      ]
       
   Example Request: get_weather_forecast("New York")
    
   Example Response:
   "weather": [
      {
         "id": 501,
         "main": "Rain",
         "description": "moderate rain",
         "icon": "10d"
      }
   ]
   
6. Route: /get-current-visbility
   Request Type: GET
   Purpose: Retrieves visibility weather data for a user's favorite location.
   Response Format: JSON
       Success Response Example: "visibility": 10000
       
   Example Request: get_current_visibility("New York")
    
   Example Response: "visibility": 10000

7. Route: /get-current-clouds
   Request Type: GET
   Purpose: Retrieves cloud weather data for a user's favorite location.
   Response Format: JSON
       Success Response Example:
       "clouds": {
         "all": 83
      }
       
   Example Request: get_current_clouds("New York")
    
   Example Response:
   "clouds": {
      "all": 83
   }

8. Route: /get-current-wind
   Request Type: GET
   Purpose: Retrieves wind weather data for a user's favorite location.
   Response Format: JSON
       Success Response Example: 
      "wind": {
         "speed": 4.09,
         "deg": 121,
         "gust": 3.47
      }
       
   Example Request: get_current_wind("New York")
    
   Example Response:
   "wind": {
      "speed": 4.09,
      "deg": 121,
      "gust": 3.47
   }
