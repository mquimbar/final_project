from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from models.weather_model import get_current_weather, get_weather_forecast
from models.favorites_model import add_favorite_city, get_favorite_cities, delete_favorite_city
from models.user_model import Users
from utils.sql_utils import check_database_connection, check_table_exists
import logging
from utils.db import db
from config import ProductionConfig

# Load environment variables from .env file
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

def create_app(config_class=ProductionConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)  # Initialize db with app
    with app.app_context():
        db.create_all()  # Recreate all tables

    return app
    #battle_model = BattleModel()


####################################################
# Health Checks
####################################################


@app.route('/api/health', methods=['GET'])
def healthcheck():
    """Health check route to verify the service is running."""
    app.logger.info('Health check passed.')
    return make_response(jsonify({'status': 'healthy'}), 200)

@app.route('/api/db-check', methods=['GET'])
def db_check():
    """Check database connection and verify the favorites table exists."""
    try:
        check_database_connection()
        check_table_exists("favorites")
        check_table_exists("users")  # Ensure users table exists
        return make_response(jsonify({'database_status': 'healthy'}), 200)
    except Exception as e:
        app.logger.error(f"Database error: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


####################################################
# User Authentication
####################################################


@app.route('/api/create-account', methods=['POST'])
def create_account():
    """Create a new user account."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return make_response(jsonify({'error': 'Username and password are required'}), 400)

        Users.create_user(username, password)
        return make_response(jsonify({'message': 'User account created successfully'}), 201)
    except Exception as e:
        app.logger.error(f"Error creating account: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/login', methods=['POST'])
def login():
    """Verify user credentials."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return make_response(jsonify({'error': 'Username and password are required'}), 400)

        if Users.login_user(username, password):
            return make_response(jsonify({'message': 'Login successful'}), 200)
        else:
            return make_response(jsonify({'error': 'Invalid credentials'}), 401)
    except Exception as e:
        app.logger.error(f"Error logging in: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/update-password', methods=['POST'])
def update_password():
    """Update a user's password."""
    try:
        data = request.get_json()
        username = data.get('username')
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not username or not old_password or not new_password:
            return make_response(jsonify({'error': 'All fields are required'}), 400)

        if Users.update_password(username, old_password, new_password):
            return make_response(jsonify({'message': 'Password updated successfully'}), 200)
        else:
            return make_response(jsonify({'error': 'Invalid credentials'}), 401)
    except Exception as e:
        app.logger.error(f"Error updating password: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


####################################################
# Favorite Cities
####################################################


@app.route('/api/add-favorite', methods=['POST'])
def add_favorite():
    """Add a city to the user's list of favorite cities."""
    try:
        data = request.get_json()
        user = data.get('user')
        city = data.get('city')

        if not user or not city:
            return make_response(jsonify({'error': 'Both user and city are required'}), 400)

        add_favorite_city(user, city)
        return make_response(jsonify({'message': f'{city} added to favorites for user {user}'}), 201)
    except Exception as e:
        app.logger.error(f"Error adding favorite: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get-favorites/<string:user>', methods=['GET'])
def get_favorites(user):
    """Retrieve all favorite cities for a user."""
    try:
        favorites = get_favorite_cities(user)
        return make_response(jsonify({'user': user, 'favorites': favorites}), 200)
    except Exception as e:
        app.logger.error(f"Error retrieving favorites: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/delete-favorite', methods=['DELETE'])
def delete_favorite():
    """Delete a city from the user's favorites."""
    try:
        data = request.get_json()
        user = data.get('user')
        city = data.get('city')

        if not user or not city:
            return make_response(jsonify({'error': 'Both user and city are required'}), 400)

        delete_favorite_city(user, city)
        return make_response(jsonify({'message': f'{city} removed from favorites for user {user}'}), 200)
    except Exception as e:
        app.logger.error(f"Error deleting favorite: {e}")
        return make_response(jsonify({'error': str(e)}), 500)


####################################################
# Weather Data
####################################################


@app.route('/api/weather/<string:city>', methods=['GET'])
def get_weather(city):
    """Retrieve current weather data for a city."""
    try:
        weather = get_current_weather(city)
        return make_response(jsonify(weather), 200)
    except Exception as e:
        app.logger.error(f"Error fetching weather: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/forecast/<string:city>', methods=['GET'])
def get_forecast(city):
    """Retrieve weather forecast data for a city."""
    try:
        forecast = get_weather_forecast(city)
        return make_response(jsonify(forecast), 200)
    except Exception as e:
        app.logger.error(f"Error fetching forecast: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)