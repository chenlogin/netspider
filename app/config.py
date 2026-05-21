import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DB_PATH = os.getenv("DB_PATH", str(BASE_DIR / "data" / "netspider.db"))

# Crawler settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
MAX_CONCURRENCY = int(os.getenv("MAX_CONCURRENCY", "3"))
USER_AGENT = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
)

# Data sources (enabled sources will be queried)
DATA_SOURCES = ["qichacha_mock"]  # replace with real sources when available
