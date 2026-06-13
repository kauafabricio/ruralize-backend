import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ruralize")

def _normalize_mongo_url(url: str) -> str:
    if url.startswith("mongodb://localhost"):
        return url.replace("localhost", "127.0.0.1")
    return url

MONGO_URL = _normalize_mongo_url(
    os.getenv("MONGO_URL", f"mongodb://127.0.0.1:27017/{MONGO_DB_NAME}")
)
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# SMTP Configuration for Email Service
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "ruralizecontato@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

# Validate SMTP configuration
if not SMTP_PASSWORD:
    import warnings
    warnings.warn(
        "SMTP_PASSWORD is not configured. Email functionality will not work. "
        "Please set SMTP_PASSWORD environment variable."
    )