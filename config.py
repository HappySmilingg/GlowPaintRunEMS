import os

class Config:
    # About MySQL Database
    SECRET_KEY = os.urandom(24)
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
