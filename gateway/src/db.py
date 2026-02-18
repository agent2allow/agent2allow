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


def run_startup_migrations() -> None:
    if not settings.database_url.startswith("sqlite:///"):
        return
    with engine.begin() as connection:
        result = connection.exec_driver_sql("PRAGMA table_info(audit_logs)")
        columns = {row[1] for row in result.fetchall()}
        if "schema_version" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE audit_logs ADD COLUMN schema_version INTEGER NOT NULL DEFAULT 1"
            )
