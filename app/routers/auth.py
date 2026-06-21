"""Routes d'authentification : connexion et profil courant."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.models import Role, User
from app.security import (
    create_access_token,
    get_current_user,
    require_roles,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> schemas.Token:
    """Authentifie un utilisateur (champ `username` = email) et renvoie un JWT."""
    user = crud.get_user_by_email(db, form_data.username)
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    token = create_access_token(subject=user.email, role=user.role.value)
    return schemas.Token(access_token=token)


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post(
    "/users",
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Role.admin))],
)
def create_user(
    data: schemas.UserCreate,
    db: Session = Depends(get_db),
) -> User:
    """Crée un nouvel utilisateur (réservé à l'administrateur)."""
    if crud.get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Un utilisateur avec cet email existe déjà",
        )
    return crud.create_user(db, data)
