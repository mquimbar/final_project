from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from models.weather_model import WeatherModel
from models.favorites_model import FavoritesModel
from models.user_model import Users
from utils.sql_utils import check_database_connection, check_table_exists
import logging
from db import db
from config import ProductionConfig
from models.mongo_session_model import login_user, logout_user
from werkzeug.exceptions import BadRequest, Unauthorized

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
    #favorites_model = FavoritesModel()


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


@app.route('/api/create-user', methods=['POST'])
def create_user() -> Response:
        """
        Route to create a new user.

        Expected JSON Input:
            - username (str): The username for the new user.
            - password (str): The password for the new user.

        Returns:
            JSON response indicating the success of user creation.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the user to the database.
        """
        app.logger.info('Creating new user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return make_response(jsonify({'error': 'Invalid input, both username and password are required'}), 400)

            # Call the User function to add the user to the database
            app.logger.info('Adding user: %s', username)
            Users.create_user(username, password)

            app.logger.info("User added: %s", username)
            return make_response(jsonify({'status': 'user added', 'username': username}), 201)
        except Exception as e:
            app.logger.error("Failed to add user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)
    
@app.route('/api/delete-user', methods=['DELETE'])
def delete_user() -> Response:
        """
        Route to delete a user.

        Expected JSON Input:
            - username (str): The username of the user to be deleted.

        Returns:
            JSON response indicating the success of user deletion.
        Raises:
            400 error if input validation fails.
            500 error if there is an issue deleting the user from the database.
        """
        app.logger.info('Deleting user')
        try:
            # Get the JSON data from the request
            data = request.get_json()

            # Extract and validate required fields
            username = data.get('username')

            if not username:
                return make_response(jsonify({'error': 'Invalid input, username is required'}), 400)

            # Call the User function to delete the user from the database
            app.logger.info('Deleting user: %s', username)
            Users.delete_user(username)

            app.logger.info("User deleted: %s", username)
            return make_response(jsonify({'status': 'user deleted', 'username': username}), 200)
        except Exception as e:
            app.logger.error("Failed to delete user: %s", str(e))
            return make_response(jsonify({'error': str(e)}), 500)


@app.route('/api/login', methods=['POST'])
def login():
        """
        Route to log in a user and load their combatants.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The user's password.

        Returns:
            JSON response indicating the success of the login.

        Raises:
            400 error if input validation fails.
            401 error if authentication fails (invalid username or password).
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            app.logger.error("Invalid request payload for login.")
            raise BadRequest("Invalid request payload. 'username' and 'password' are required.")

        username = data['username']
        password = data['password']

        try:
            # Validate user credentials
            if not Users.check_password(username, password):
                app.logger.warning("Login failed for username: %s", username)
                raise Unauthorized("Invalid username or password.")

            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Load user's combatants into the battle model
            login_user(user_id, FavoritesModel)

            app.logger.info("User %s logged in successfully.", username)
            return jsonify({"message": f"User {username} logged in successfully."}), 200

        except Unauthorized as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            app.logger.error("Error during login for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
        """
        Route to log out a user and save their combatants to MongoDB.

        Expected JSON Input:
            - username (str): The username of the user.

        Returns:
            JSON response indicating the success of the logout.

        Raises:
            400 error if input validation fails or user is not found in MongoDB.
            500 error for any unexpected server-side issues.
        """
        data = request.get_json()
        if not data or 'username' not in data:
            app.logger.error("Invalid request payload for logout.")
            raise BadRequest("Invalid request payload. 'username' is required.")

        username = data['username']

        try:
            # Get user ID
            user_id = Users.get_id_by_username(username)

            # Save user's combatants and clear the battle model
            logout_user(user_id, FavoritesModel)

            app.logger.info("User %s logged out successfully.", username)
            return jsonify({"message": f"User {username} logged out successfully."}), 200

        except ValueError as e:
            app.logger.warning("Logout failed for username %s: %s", username, str(e))
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            app.logger.error("Error during logout for username %s: %s", username, str(e))
            return jsonify({"error": "An unexpected error occurred."}), 500


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

        FavoritesModel.add_favorite_city(user, city)
        return make_response(jsonify({'message': f'{city} added to favorites for user {user}'}), 201)
    except Exception as e:
        app.logger.error(f"Error adding favorite: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/get-favorites/<string:user>', methods=['GET'])
def get_favorites(user):
    """Retrieve all favorite cities for a user."""
    try:
        favorites = FavoritesModel.get_favorite_cities(user)
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

        FavoritesModel.delete_favorite_city(user, city)
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
        weather = WeatherModel.get_current_weather(city)
        return make_response(jsonify(weather), 200)
    except Exception as e:
        app.logger.error(f"Error fetching weather: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

@app.route('/api/forecast/<string:city>', methods=['GET'])
def get_forecast(city):
    """Retrieve weather forecast data for a city."""
    try:
        forecast = WeatherModel.get_weather_forecast(city)
        return make_response(jsonify(forecast), 200)
    except Exception as e:
        app.logger.error(f"Error fetching forecast: {e}")
        return make_response(jsonify({'error': str(e)}), 500)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)