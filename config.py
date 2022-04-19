import os

# options = 'development' | 'production' (default)
profile = os.environ.get('PROFILE', 'production')

class Config:
    placeholder = 0

class DevConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    placeholder = 1

config = DevConfig if profile == 'development' else ProductionConfig
