import os


class Settings:
    DATABASE_URL = os.environ.get("DATABASE_URL")


settings = Settings()
