import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'
    
    # Correct MySQL URI format: mysql+pymysql://username:password@host/database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://root:vishnu%40123@localhost/chat_db'  # use '%40' for '@' in password
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
