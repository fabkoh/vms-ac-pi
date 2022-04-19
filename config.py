class Config:
    placeholder = 0

class DevConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    placeholder = 1

config = {
    'development': DevConfig,
    'production': ProductionConfig
}
