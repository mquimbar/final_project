from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from final_project.models.weather_model import WeatherModel
from final_project.models.favorites_model import FavoritesModel
from final_project.models.user_model import Users
#from utils.sql_utils import check_database_connection, check_table_exists
import logging
from final_project.db import db
from config import ProductionConfig
from final_project.models.mongo_session_model import login_user, logout_user
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

    favorites_model = FavoritesModel() # **********


####################################################
# Health Checks
####################################################


    @app.route('/api/health', methods=['GET'])
    def healthcheck():
        """
        Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.
        """
        app.logger.info('Health check')
        return make_response(jsonify({'status': 'healthy'}), 200)

    # @app.route('/api/db-check', methods=['GET'])
    # def db_check():
    #     """Check database connection and verify the favorites table exists."""
    #     try:
    #         check_database_connection()
    #         check_table_exists("favorites")
    #         check_table_exists("users")  # Ensure users table exists
    #         return make_response(jsonify({'database_status': 'healthy'}), 200)
    #     except Exception as e:
    #         app.logger.error(f"Database error: {e}")
    #         return make_response(jsonify({'error': str(e)}), 500)


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
                login_user(user_id, favorites_model) # ************

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
                logout_user(user_id, favorites_model)

                app.logger.info("User %s logged out successfully.", username)
                return jsonify({"message": f"User {username} logged out successfully."}), 200

            except ValueError as e:
                app.logger.warning("Logout failed for username %s: %s", username, str(e))
                return jsonify({"error": str(e)}), 400
            except Exception as e:
                app.logger.error("Error during logout for username %s: %s", username, str(e))
                return jsonify({"error": "An unexpected error occurred."}), 500


    ####################################################
    # Favorite Cities
    ####################################################


    @app.route('/api/add-favorite', methods=['POST'])
    def add_favorite():
        """
            Route to add a new city to the database.

            Expected JSON Input:
                - user (str): The user.
                - city (str): The name of the city.

            Returns:
                JSON response indicating the success of the city addition.
            Raises:
                400 error if input validation fails.
                500 error if there is an issue adding the combatant to the database.
            """
        try:
            data = request.get_json()
            #user = data.get('user')
            city = data.get('city')
            #print(data, user, city)

            if not city:
                return make_response(jsonify({'error': 'City is required'}), 400)

            favorites_model.add_favorite_city(city)
            return make_response(jsonify({'message': f'{city} added to favorites'}), 201)
        except Exception as e:
            app.logger.error(f"Error adding favorite: {e}")
            return make_response(jsonify({'error': str(e)}), 500)

    @app.route('/api/get-favorites/<string:user>', methods=['GET'])
    def get_favorites(user):
        """Retrieve all favorite cities for a user."""
        try:
            favorites = favorites_model.get_favorite_cities(user)
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

            favorites_model.delete_favorite_city(user, city)
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
        
    @app.route('/api/init-db', methods=['POST'])
    def init_db():
            """
            Initialize or recreate database tables.

            This route initializes the database tables defined in the SQLAlchemy models.
            If the tables already exist, they are dropped and recreated to ensure a clean
            slate. Use this with caution as all existing data will be deleted.

            Returns:
                Response: A JSON response indicating the success or failure of the operation.

            Logs:
                Logs the status of the database initialization process.
            """
            try:
                with app.app_context():
                    app.logger.info("Dropping all existing tables.")
                    db.drop_all()  # Drop all existing tables
                    app.logger.info("Creating all tables from models.")
                    db.create_all()  # Recreate all tables
                app.logger.info("Database initialized successfully.")
                return jsonify({"status": "success", "message": "Database initialized successfully."}), 200
            except Exception as e:
                app.logger.error("Failed to initialize database: %s", str(e))
                return jsonify({"status": "error", "message": "Failed to initialize database."}), 500
            
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8080)