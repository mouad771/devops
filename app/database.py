"""Configuration de la connexion à la base de données via SQLAlchemy."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# SQLite nécessite un argument spécifique pour fonctionner avec plusieurs threads
# (cas du serveur de tests). PostgreSQL n'en a pas besoin.
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Classe de base déclarative pour les modèles ORM."""


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI fournissant une session de base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
