import logging
from typing import List
from utils.sql_utils import get_db_connection

logger = logging.getLogger(__name__)

def add_favorite_city(user: str, city: str) -> None:
    """
    Add a favorite city for a user to the database.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO favorites (user, city) VALUES (?, ?)", (user, city))
            conn.commit()
            logger.info("added favorite city: %s", city)
    except Exception as e:
        logger.error(f"Error adding favorite city: {e}")
        raise e

def get_favorite_cities(user: str) -> List[str]:
    """
    Retrieve all favorite cities for a user.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city FROM favorites WHERE user = ?", (user,))
            logger.info("got the list of favorite cities!")
            return [row[0] for row in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error retrieving favorite cities: {e}")
        raise e

def delete_favorite_city(user: str, city: str) -> None:
    """
    Delete a favorite city for a user from the database.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM favorites WHERE user = ? AND city = ?", (user, city))
            conn.commit()
            logger.info("deleted favorite city: %s", city)
    except Exception as e:
        logger.error(f"Error deleting favorite city: {e}")
        raise e
