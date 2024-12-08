import logging
import os
import time
from typing import Any, List
from final_project.utils.logger import configure_logger
from final_project.db import db
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError
from final_project.clients.redis_client import redis_client
from dataclasses import asdict, dataclass
#from final_project.utils.sql_utils import get_db_connection

logger = logging.getLogger(__name__)
configure_logger(logger)

@dataclass
class FavoritesModel(db.Model):
    __tablename__ = 'favorites'

    id: int = db.Column(db.Integer, primary_key=True)
    city: str = db.Column(db.String(80), unique=True, nullable=False)
    #user: str = db.Column(db.String(80), unique=True, nullable=False)
    #maybe need user????

    # def __init__(self):
    #     """Initializes the BattleManager with an empty list of combatants and TTL."""
    #     self.city: str  # List of active combatants

    @classmethod
    def add_favorite_city(cls, city: str) -> None:
        """
        Create a new city in the database.

        Args:
            city (str): The name of the city.

        Raises:
            ValueError: If a meal with the same name exists.
            IntegrityError: If there is a database error.
        """
        new_city = cls(city=city)
        try:
            db.session.add(new_city)
            db.session.commit()
            logger.info("City successfully added to the database: %s", city)
        except Exception as e:
            db.session.rollback()
            if isinstance(e, IntegrityError):
                logger.error("Duplicate city name: %s", city)
                raise ValueError(f"City with name '{city}' already exists")
            else:
                logger.error("Database error: %s", str(e))
                raise

    @classmethod
    def get_favorite_cities(cls, city: str) -> List[str]:
        """
        Retrieve cities.

        Args:
            city (str): The name of the city.

        Returns:
            dict: The city data as a list.

        Raises:
            ValueError: If the city does not exist or is deleted.
        """
        logger.info("Retrieving city: %s", city)
        cache_key = f"{city}"
        cached_city = redis_client.hgetall(cache_key)
        if cached_city:
            logger.info("City retrieved from cache: %s", city)
            city_data = {k.decode(): v.decode() for k, v in cached_city.items()}
            #city_data["price"] = float(meal_data["price"]) ??????
            # meal_data['deleted'] is a string. We need to convert it to a bool
            city_data['deleted'] = city_data.get('deleted', 'false').lower() == 'true'
            if city_data['deleted']:
                logger.info("Meal with name %s not found", city)
                raise ValueError(f"Meal {city} not found")
            return city_data
        #meal = cls.query.filter_by(id=meal_id).first()
        # if not meal or meal.deleted:
        #     logger.info("Meal with %s %s not found", "name" if meal_name else "ID", meal_name or meal_id)
        #     raise ValueError(f"Meal {meal_name or meal_id} not found")
        # Convert the meal object to a dictionary and cache it
        logger.info("City retrieved from database and cached: %s", city)
        city_dict = asdict(city) # ?????? change this to list??????
        redis_client.hset(cache_key, mapping={k: str(v) for k, v in city_dict.items()})
        return city_dict

    @classmethod
    def delete_favorite_city(cls, city: str) -> None:
        """
        Soft delete a city by marking it as deleted.

        Args:
            city (str): The name of the city to delete.

        Raises:
            ValueError: If the city with the given ID does not exist or is already deleted.
        """
        city_check = cls.query.filter_by(city=city).first()
        if not city_check:
            logger.info("City %s not found", city)
            raise ValueError(f"City {city} not found")
        if city_check.deleted:
            logger.info("City with name %s has already been deleted", city)
            raise ValueError(f"City with name {city} has been deleted")

        city_check.deleted = True
        db.session.commit()
        logger.info("City with name %s marked as deleted.", city)
