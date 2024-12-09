#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:8080/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  #echo "$(curl -s -X GET "$BASE_URL/health")"
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

##############################################
#
# User management
#
##############################################

# Function to create a user
create_user() {
  echo "Creating a new user..."
  curl -s -X POST "$BASE_URL/create-user" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}' | grep -q '"status": "user added"'
  echo "$(curl -s -X POST "$BASE_URL/create-user" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')"
  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user."
    exit 1
  fi
}

# Function to log in a user
login_user() {
  echo "Logging in user..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')
  #echo "$response"
  if echo "$response" | grep -q '"message": "User testuser logged in successfully."'; then
    echo "User logged in successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log in user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

# Function to log out a user
logout_user() {
  echo "Logging out user..."
  response=$(curl -s -X POST "$BASE_URL/logout" -H "Content-Type: application/json" \
    -d '{"username":"testuser"}')
  if echo "$response" | grep -q '"message": "User testuser logged out successfully."'; then
    echo "User logged out successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Logout Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log out user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

##############################################
#
# Favorite Cities
#
##############################################

# Function to add a favorite city
add_favorite_city() {
  echo "Adding a favorite city..."
  response=$(curl -s -X POST "$BASE_URL/add-favorite" -H "Content-Type: application/json" \
    -d '{"city":"NewYork"}')
  echo "$response"
  if echo "$response" | grep -q '"message": "NewYork added to favorites'; then
    echo "Favorite city added successfully."
  else
    echo "Failed to add favorite city."
    exit 1
  fi
}

# Function to get favorite cities
get_favorites() {
  echo "Retrieving favorite cities..."
  response=$(curl -s -X GET "$BASE_URL/get-favorites/testuser")
  echo "$response"
  if echo "$response" | grep -q '"favorites"'; then
    echo "Favorite cities retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Favorites JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve favorite cities."
    exit 1
  fi
}

# Function to delete a favorite city
delete_favorite_city() {
  echo "Deleting a favorite city..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-favorite" -H "Content-Type: application/json" \
    -d '{"city":"NewYork"}')
  echo "$response"
  if echo "$response" | grep -q '"message": "NewYork removed from favorites'; then
    echo "Favorite city deleted successfully."
  else
    echo "Failed to delete favorite city."
    exit 1
  fi
}

##############################################
#
# Weather Data
#
##############################################

# Function to get current weather for a city
get_weather() {
  echo "Getting current weather for New York..."
  response=$(curl -s -X GET "$BASE_URL/weather/New York")
  if echo "$response" | grep -q '"temperature"'; then
    echo "Weather data retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Weather JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve weather data."
    exit 1
  fi
}

# Function to get weather forecast for a city
get_forecast() {
  echo "Getting weather forecast for New York..."
  response=$(curl -s -X GET "$BASE_URL/forecast/New York")
  if echo "$response" | grep -q '"forecast"'; then
    echo "Weather forecast retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Forecast JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve weather forecast."
    exit 1
  fi
}

##############################################
#
# Run All Tests
#
##############################################

# Run all the tests in order
check_health
create_user
login_user
delete_favorite_city
add_favorite_city
get_favorites
delete_favorite_city
get_weather
get_forecast

echo "All tests passed successfully!"