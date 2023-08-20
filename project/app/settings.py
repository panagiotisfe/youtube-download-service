import os


class Settings:
    DATABASE_URL = os.environ.get("DATABASE_URL")
    REDIS_URL = os.environ.get("REDIS_URL")
    REDIS_TTL = 60 * 10  # seconds
    MAX_VIDEO_LENGTH = 60 * 10  # seconds


settings = Settings()
