import sqlite3
import os
import hashlib
import hmac
from cryptography.fernet import Fernet

DB_NAME = "users.db"
SCHEMA_FILE = "schema.sql"
KEY_FILE = ".secret.key"


def hash_password(password: str) -> tuple[bytes, bytes]:
    '''
    Hashes a password using PBKDF2 with SHA-256 and a random salt.
    '''
    salt = os.urandom(16)
    hashed_password = hashlib.pbkdf2_hmac(
        hash_name = 'sha256',
        password = password.encode('utf-8'),
        salt = salt,
        iterations=60000
    )
    return hashed_password, salt

def verify_password(stored_salt: bytes, hashed_pass: bytes, input_pass: str) -> bool:
    new_hash_pass = hashlib.pbkdf2_hmac(
        hash_name = 'sha256',
        password = input_pass.encode('utf-8'),
        salt = stored_salt,
        iterations = 60000
    )
    return hmac.compare_digest(hashed_pass, new_hash_pass)

def load_key():
    '''
    Load the Fernet key from a file or generate a new one if it doesn't exist.    
    '''
    if not os.path.exists(KEY_FILE):
        new_key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as file:
            file.write(new_key)
        return new_key
    
    else:
        with open(KEY_FILE, "rb") as file:
            return file.read()

MASTER_KEY = load_key()
cipher_suite = Fernet(MASTER_KEY)

def encrypt_api_key(api_key: str | None) -> str | None:
    if not api_key:
        return None
    
    return cipher_suite.encrypt(api_key.encode('utf-8')).decode('utf-8')

def decrypt_api_key(encrypted_api_key: str | None) -> str | None:
    if not encrypted_api_key:
        return None
    
    return cipher_suite.decrypt(encrypted_api_key.encode('utf-8')).decode('utf-8')

def init_auth_db():
    '''
    Initialize the SQLite database and create the App_Users table if it doesn't exist.
    '''
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    try:
        if os.path.exists(SCHEMA_FILE):
            with open(SCHEMA_FILE, "r") as file:
                schema_sql = file.read()
            cursor.executescript(schema_sql)
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS App_Users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash BLOB NOT NULL,
                    password_salt BLOB NOT NULL,
                    kaggle_username TEXT,
                    encrypted_api_key TEXT
                    );
            """)
        connection.commit()
    except Exception as e:
        print(f"Failed to set up database: {e}")
    finally:
        connection.close()

def register_user(username, password, kaggle_username=None, api_key = None):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    user_hashed_pass, user_salt = hash_password(password)
    api_key_encrypted = encrypt_api_key(api_key)

    try:
        cursor.execute("""
            INSERT INTO App_Users (username, password_hash, password_salt, kaggle_username, encrypted_api_key)
            VALUES (?, ?, ?, ?, ?)
        """, (username, user_hashed_pass, user_salt, kaggle_username, api_key_encrypted))
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        connection.close()

def verify_user(username: str, password: str):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    #Get stored password information to validate for given username
    cursor.execute("""
        SELECT id, password_hash, password_salt FROM App_Users WHERE username = ?
    """, (username,))

    user = cursor.fetchone()
    connection.close()

    if user:
        user_id, stored_hash, stored_salt = user

        if verify_password(stored_salt, stored_hash, password):
            return user_id
        
    return None

def get_encrypted_user_api(user_id):
    '''
    Retrieve the Kaggle username and decrypted API key for a given user ID.
    '''
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT kaggle_username, encrypted_api_key FROM App_Users where id = ?
    """, (user_id,))

    result = cursor.fetchone()
    connection.close()

    if result:
        kaggle_username, encrypted_key = result
        decrypted_key = decrypt_api_key(encrypted_key)

        return kaggle_username, decrypted_key
    
    return None, None

