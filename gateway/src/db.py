from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .settings import settings

if settings.database_url.startswith("sqlite:///"):
    db_path = settings.database_url.replace("sqlite:///", "", 1)
    if db_path.startswith("./"):
        Path(db_path[2:]).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
