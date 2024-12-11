import pytest
from final_project.models.favorites_model import FavoritesModel

@pytest.fixture
def sample_city():
    return "Boston"

##########################################################
# Add Favorite City
##########################################################

def test_add_favorite_city(session, sample_city):
    """Test adding a favorite city."""
    FavoritesModel.add_favorite_city(sample_city)
    city = session.query(FavoritesModel).filter_by(city=sample_city).first()
    assert city is not None, "City should be added to the database."
    assert city.city == sample_city, "City name should match the input."

def test_add_duplicate_favorite_city(session, sample_city):
    """Test attempting to add a duplicate city."""
    FavoritesModel.add_favorite_city(sample_city)
    with pytest.raises(ValueError, match=f"City with name '{sample_city}' already exists"):
        FavoritesModel.add_favorite_city(sample_city)

##########################################################
# Get Favorite Cities
##########################################################

def test_get_favorite_cities(session):
    """Test retrieving favorite cities."""
    FavoritesModel.add_favorite_city("Boston")
    FavoritesModel.add_favorite_city("New York")

    cities = session.query(FavoritesModel.city).all()
    city_names = [city[0] for city in cities]

    assert "Boston" in city_names, "Boston should be in the list of favorite cities."
    assert "New York" in city_names, "New York should be in the list of favorite cities."

##########################################################
# Delete Favorite City
##########################################################

def test_delete_favorite_city(session, sample_city):
    """Test deleting a favorite city."""
    FavoritesModel.add_favorite_city(sample_city)
    city = session.query(FavoritesModel).filter_by(city=sample_city).first()
    assert city is not None, "City should exist before deletion."

    FavoritesModel.delete_favorite_city(city.id)
    city = session.query(FavoritesModel).filter_by(city=sample_city).first()
    assert city.deleted is True, "City should be marked as deleted."


def test_delete_nonexistent_favorite_city(session):
    """Test attempting to delete a city that does not exist."""
    with pytest.raises(ValueError, match="City 999 not found"):
        FavoritesModel.delete_favorite_city(999)
