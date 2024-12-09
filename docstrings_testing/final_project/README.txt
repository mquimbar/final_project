Weather Dashboard Application

Overview:
The Weather Dashboard is a web-based application designed to provide users with easy access to weather information. 
This application allows users to set favorite locations and quickly view current, forecasted, and historical weather data for these locations. 
By offering userspecific customization, the Weather Dashboard aims to deliver a personalized weather tracking experience, 
making it easier for users to get the most relevant weather information based on their interests and needs. 

Features & Routes:

1. Route: /set-favorite-location
   Request Type: POST
   Purpose: Allows users to save a location as a favorite.
   Request Body: location (String): Name of the city or area to be added to favorites.
   Response Format: JSON
        Success Response Example: 
        
   Example Request:

   Example Response:


2. Route: /get-weather
   Request Type: GET
   Purpose: Fetches the current weather details for a saved favorite location.
   Response Format: JSON
       Success Response Example:
       
   Example Request:
    
   Example Response:
    

3. Route: /view-all-favorites
   Request Type: GET
   Purpose: Retrieves the list of all saved favorite locations along with their current weather data.
   Response Format: JSON
       Success Response Example:
       
   Example Request:
    
   Example Response:


4. Route: /get-historical-weather
   Request Type: GET
   Purpose: Retrieves historical weather data for a user's favorite location.
   Response Format: JSON
       Success Response Example:
       
   Example Request:
    
   Example Response:
   
5. Route: /get-forecast
   Request Type: GET
   Purpose: Retrieves weather forecast for a user's favorite location.
   Response Format: JSON
       Success Response Example:
       
   Example Request:
    
   Example Response:
