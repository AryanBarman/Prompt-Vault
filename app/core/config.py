import os
from dotenv import load_dotenv

ENV = os.getenv("ENV", "development")
IS_PROD = ENV == "production"

# Load environment variables from .env file
load_dotenv()

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretekeyhere-CHANGE-IN-PRODUCTION")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
EXPIRE_MINUTES = int(os.getenv("EXPIRE_MINUTES", "30"))

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
