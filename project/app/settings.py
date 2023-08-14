import os


class Settings:
    DOWNLOAD_PATH = os.getenv("DOWNLOAD_PATH")


settings = Settings()
