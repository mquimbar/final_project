import pytest
from unittest.mock import patch, MagicMock
from final_project.models.favorites_model import FavoritesModel


@pytest.fixture
def favorites_model():
    """Fixture to provide a new instance of BattleModel for each test."""
    return FavoritesModel()

@patch("models.favorites_model.get_db_connection")
def test_add_favorite_city(mock_db_conn):
    mock_conn = MagicMock()
    mock_db_conn.return_value.__enter__.return_value = mock_conn
    favorites_model.add_favorite_city("user1", "Boston")
    mock_conn.cursor().execute.assert_called_once_with(
        "INSERT INTO favorites (user, city) VALUES (?, ?)", ("user1", "Boston")
    )
    mock_conn.commit.assert_called_once()


@patch("models.favorites_model.get_db_connection")
def test_get_favorite_cities(mock_db_conn):
    mock_conn = MagicMock()
    mock_db_conn.return_value.__enter__.return_value = mock_conn
    mock_conn.cursor().fetchall.return_value = [("Boston",), ("New York",)]
    cities = favorites_model.get_favorite_cities("user1")
    assert cities == ["Boston", "New York"]
    mock_conn.cursor().execute.assert_called_once_with(
        "SELECT city FROM favorites WHERE user = ?", ("user1",)
    )


@patch("models.favorites_model.get_db_connection")
def test_delete_favorite_city(mock_db_conn):
    mock_conn = MagicMock()
    mock_db_conn.return_value.__enter__.return_value = mock_conn
    favorites_model.delete_favorite_city("user1", "Boston")
    mock_conn.cursor().execute.assert_called_once_with(
        "DELETE FROM favorites WHERE user = ? AND city = ?", ("user1", "Boston")
    )
    mock_conn.commit.assert_called_once()

