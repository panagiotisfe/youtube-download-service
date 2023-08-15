import os


class Settings:
    DATABASE_URL = os.environ.get("DATABASE_URL")
    MAX_VIDEO_LENGTH = 60 * 10  # seconds


settings = Settings()
