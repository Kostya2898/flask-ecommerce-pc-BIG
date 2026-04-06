import os
from datetime import timedelta

class Config:
    """Базова конфігурація"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'igrofix-pc-super-secret-key-2024'
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///igrofix.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Завантаження файлів
    UPLOAD_FOLDER = os.path.join('static', 'images', 'products')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Пагінація
    ITEMS_PER_PAGE = 12
    
    # Кошик
    CART_SESSION_KEY = 'cart'

class DevelopmentConfig(Config):
    """Конфігурація для розробки"""
    DEBUG = True

class ProductionConfig(Config):
    """Конфігурація для продакшену"""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
