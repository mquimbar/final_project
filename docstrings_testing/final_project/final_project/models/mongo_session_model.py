import logging
from typing import Any, List

from final_project.clients.mongo_client import sessions_collection
from final_project.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


def login_user(user_id: int, favorites_model) -> None:
    """
    Load the user's combatants from MongoDB into the BattleModel's combatants list.

    Checks if a session document exists for the given `user_id` in MongoDB.
    If it exists, clears any current favorites in `favorites_model` and loads
    the stored favorites from MongoDB into `favorites_model`.

    If no session is found, it creates a new session document for the user
    with an empty combatants list in MongoDB.

    Args:
        user_id (int): The ID of the user whose session is to be loaded.
        favorites_model (BattleModel): An instance of `BattleModel` where the user's combatants
                                    will be loaded.
    """
    logger.info("Attempting to log in user with ID %d.", user_id)
    session = sessions_collection.find_one({"user_id": user_id})

    if session:
        logger.info("Session found for user ID %d. Loading cities.", user_id)
        #favorites_model.clear_favorites() # *******
        for city in session.get("cities", []):
            logger.debug("Addding favorite: %s", city)
            favorites_model.add_favorite_city(city)
        logger.info("Favorites successfully loaded for user ID %d.", user_id)
    else:
        logger.info("No session found for user ID %d. Creating a new session with empty favorites list.", user_id)
        sessions_collection.insert_one({"user_id": user_id, "favorites": []})
        logger.info("New session created for user ID %d.", user_id)

def logout_user(user_id: int, favorites_model) -> None:
    """
    Store the current combatants from the BattleModel back into MongoDB.

    Retrieves the current combatants from `battle_model` and attempts to store them in
    the MongoDB session document associated with the given `user_id`. If no session
    document exists for the user, raises a `ValueError`.

    After saving the combatants to MongoDB, the combatants list in `battle_model` is
    cleared to ensure a fresh state for the next login.

    Args:
        user_id (int): The ID of the user whose session data is to be saved.
        battle_model (BattleModel): An instance of `BattleModel` from which the user's
                                    current combatants are retrieved.

    Raises:
        ValueError: If no session document is found for the user in MongoDB.
    """
    logger.info("Attempting to log out user with ID %d.", user_id)
    city_data = favorites_model.get_favorite_cities()
    logger.debug("Current combatants for user ID %d: %s", user_id)

    result = sessions_collection.update_one(
        {"user_id": user_id},
        {"$set": {"cities": city_data}},
        upsert=False  # Prevents creating a new document if not found
    )

    if result.matched_count == 0:
        logger.error("No session found for user ID %d. Logout failed.", user_id)
        raise ValueError(f"User with ID {user_id} not found for logout.")

    logger.info("Cities successfully saved for user ID %d. Clearing FavoritesModel cities.", user_id)
    favorites_model.delete_favorite_city()
    logger.info("FavoritesModel cities cleared for user ID %d.", user_id)