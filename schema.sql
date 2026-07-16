CREATE TABLE IF NOT EXISTS App_Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(20) UNIQUE NOT NULL,
    password_hash BLOB NOT NULL,
    password_salt BLOB NOT NULL,
    kaggle_username VARCHAR(30) UNIQUE,
    api_key_hash VARCHAR(32) UNIQUE
)