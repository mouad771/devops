"""Schémas Pydantic pour la validation des entrées/sorties de l'API."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import Role


# --- Authentification ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# --- Utilisateurs ---
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    role: Role = Role.student


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: Role
    created_at: datetime


# --- Étudiants ---
class StudentBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    student_number: str = Field(min_length=1, max_length=50)
    email: EmailStr
    program: str = Field(default="", max_length=120)


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=120)
    last_name: str | None = Field(default=None, max_length=120)
    email: EmailStr | None = None
    program: str | None = Field(default=None, max_length=120)


class StudentOut(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# --- Cours ---
class CourseCreate(BaseModel):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=160)
    credits: int = Field(default=1, ge=1, le=30)


class CourseOut(CourseCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


# --- Notes ---
class GradeCreate(BaseModel):
    course_id: int
    value: float = Field(ge=0, le=20)


class GradeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    value: float
    created_at: datetime


class GradeLine(BaseModel):
    """Ligne de relevé : note enrichie du nom et code du cours."""

    course_code: str
    course_name: str
    credits: int
    value: float


class Transcript(BaseModel):
    """Relevé de notes complet d'un étudiant."""

    student: StudentOut
    lines: list[GradeLine]
    average: float | None
