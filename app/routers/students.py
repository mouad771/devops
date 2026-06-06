"""Routes CRUD pour la gestion des fiches étudiants."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.models import Role
from app.security import require_roles

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get(
    "",
    response_model=list[schemas.StudentOut],
    dependencies=[Depends(require_roles(Role.admin, Role.teacher))],
)
def list_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list:
    return crud.list_students(db, skip=skip, limit=limit)


@router.post(
    "",
    response_model=schemas.StudentOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Role.admin))],
)
def create_student(
    data: schemas.StudentCreate,
    db: Session = Depends(get_db),
):
    if crud.get_student_by_number(db, data.student_number):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce numéro étudiant est déjà utilisé",
        )
    return crud.create_student(db, data)


@router.get(
    "/{student_id}",
    response_model=schemas.StudentOut,
    dependencies=[Depends(require_roles(Role.admin, Role.teacher))],
)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    return student


@router.put(
    "/{student_id}",
    response_model=schemas.StudentOut,
    dependencies=[Depends(require_roles(Role.admin))],
)
def update_student(
    student_id: int,
    data: schemas.StudentUpdate,
    db: Session = Depends(get_db),
):
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    return crud.update_student(db, student, data)


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_roles(Role.admin))],
)
def delete_student(student_id: int, db: Session = Depends(get_db)) -> None:
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    crud.delete_student(db, student)
