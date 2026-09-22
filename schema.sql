CREATE TABLE IF NOT EXISTS App_Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(20) UNIQUE NOT NULL,
    password_hash BLOB NOT NULL,
    password_salt BLOB NOT NULL,
    kaggle_username TEXT,
    encrypted_api_key TEXT
)