import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    BASE_URL: str = os.getenv("BASE_URL", "/parlamint-api")

settings = Settings()