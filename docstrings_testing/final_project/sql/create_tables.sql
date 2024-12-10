-- Drop existing tables if they exist
DROP TABLE IF EXISTS favorites;
DROP TABLE IF EXISTS users;
-- Create the favorites table
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    city TEXT NOT NULL,
    UNIQUE(user, city)  -- Ensure each city is only added once per user
);
-- Create the users table for secure password storage
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    salt TEXT NOT NULL,
    hashed_password TEXT NOT NULL
);

-- created tables with sqlalchemy elsewhere, not here