"""Configuration externe de l'application.

Toutes les valeurs sont surchargeables via des variables d'environnement
(ou un fichier .env), conformément à l'exigence d'un fichier de configuration
externe.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Paramètres applicatifs chargés depuis l'environnement."""

    app_name: str = "Plateforme de gestion d'étudiants"
    environment: str = "development"

    # Base de données : PostgreSQL en production, SQLite par défaut pour faciliter
    # le démarrage local et les tests.
    database_url: str = "sqlite:///./gestion_etudiants.db"

    # Sécurité / JWT
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    # Compte administrateur initial créé au démarrage (seed)
    admin_email: str = "admin@ecole.ma"
    admin_password: str = "admin1234"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Retourne une instance unique (cache) des paramètres."""
    return Settings()
