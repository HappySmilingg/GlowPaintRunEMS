import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.urandom(24)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)

    # Session configuration
    SESSION_TYPE = 'filesystem'  # Store session data on the server
    SESSION_FILE_DIR = './flask_session'
    SESSION_PERMANENT = True

    # Session cookie settings
    SESSION_COOKIE_SECURE = False  # Send cookies over HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript access to cookies
    SESSION_COOKIE_SAMESITE = 'Lax' 

    # About MySQL Database
    MAX_CONTENT_LENGTH = 64 * 1024 * 1024  
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = '1234'
    MYSQL_DB = 'gprems'
    
    # About Email
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'tankaixin02@gmail.com'
    MAIL_PASSWORD = 'tiat nhzn imzd jnpi'
