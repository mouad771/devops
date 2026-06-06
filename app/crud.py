"""Opérations de persistance (CRUD) sur la base de données."""

from sqlalchemy.orm import Session

from app import models, schemas
from app.security import hash_password


# --- Utilisateurs ---
def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, data: schemas.UserCreate) -> models.User:
    user = models.User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# --- Étudiants ---
def list_students(db: Session, skip: int = 0, limit: int = 100) -> list[models.Student]:
    return db.query(models.Student).offset(skip).limit(limit).all()


def get_student(db: Session, student_id: int) -> models.Student | None:
    return db.get(models.Student, student_id)


def get_student_by_number(db: Session, number: str) -> models.Student | None:
    return (
        db.query(models.Student)
        .filter(models.Student.student_number == number)
        .first()
    )


def create_student(db: Session, data: schemas.StudentCreate) -> models.Student:
    student = models.Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def update_student(
    db: Session, student: models.Student, data: schemas.StudentUpdate
) -> models.Student:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(student, field, value)
    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student: models.Student) -> None:
    db.delete(student)
    db.commit()


# --- Cours ---
def create_course(db: Session, data: schemas.CourseCreate) -> models.Course:
    course = models.Course(**data.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def list_courses(db: Session) -> list[models.Course]:
    return db.query(models.Course).all()


def get_course(db: Session, course_id: int) -> models.Course | None:
    return db.get(models.Course, course_id)


# --- Notes ---
def upsert_grade(
    db: Session, student_id: int, data: schemas.GradeCreate
) -> models.Grade:
    """Crée ou met à jour la note d'un étudiant pour un cours."""
    grade = (
        db.query(models.Grade)
        .filter(
            models.Grade.student_id == student_id,
            models.Grade.course_id == data.course_id,
        )
        .first()
    )
    if grade is None:
        grade = models.Grade(
            student_id=student_id, course_id=data.course_id, value=data.value
        )
        db.add(grade)
    else:
        grade.value = data.value
    db.commit()
    db.refresh(grade)
    return grade


def get_transcript(db: Session, student: models.Student) -> schemas.Transcript:
    """Construit le relevé de notes complet d'un étudiant."""
    lines: list[schemas.GradeLine] = []
    weighted_sum = 0.0
    total_credits = 0
    for grade in student.grades:
        course = grade.course
        lines.append(
            schemas.GradeLine(
                course_code=course.code,
                course_name=course.name,
                credits=course.credits,
                value=grade.value,
            )
        )
        weighted_sum += grade.value * course.credits
        total_credits += course.credits

    average = round(weighted_sum / total_credits, 2) if total_credits else None
    return schemas.Transcript(
        student=schemas.StudentOut.model_validate(student),
        lines=lines,
        average=average,
    )
