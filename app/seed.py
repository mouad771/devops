"""Initialisation des données : création du compte administrateur par défaut."""

from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import get_settings
from app.models import Role


def seed_admin(db: Session) -> None:
    """Crée le compte administrateur initial s'il n'existe pas déjà."""
    settings = get_settings()
    if crud.get_user_by_email(db, settings.admin_email) is None:
        crud.create_user(
            db,
            schemas.UserCreate(
                email=settings.admin_email,
                full_name="Administrateur",
                password=settings.admin_password,
                role=Role.admin,
            ),
        )
