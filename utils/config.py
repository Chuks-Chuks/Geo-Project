from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv
 
load_dotenv()
 
@dataclass(frozen=True)
class Settings:
    # db
    db_host: str | None = os.getenv("DB_HOST")
    db_port: str | None = os.getenv("DB_PORT")
    db_name: str | None = os.getenv("DB_NAME")
    db_user: str | None = os.getenv("DB_USER")
    db_pass: str | None = os.getenv("DB_PASS")
    db_schema: str | None = os.getenv("DB_SCHEMA")

    # coordinates
    nigeria_center: str | None = os.getenv("NIGERIA_CENTER", "9.0820,8.6753")

SETTINGS = Settings()