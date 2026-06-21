"""Routes de gestion des cours et des notes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.models import Role
from app.security import require_roles

router = APIRouter(prefix="/api", tags=["grades"])


@router.get(
    "/courses",
    response_model=list[schemas.CourseOut],
    dependencies=[Depends(require_roles(Role.admin, Role.teacher))],
)
def list_courses(db: Session = Depends(get_db)) -> list:
    return crud.list_courses(db)


@router.post(
    "/courses",
    response_model=schemas.CourseOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Role.admin))],
)
def create_course(data: schemas.CourseCreate, db: Session = Depends(get_db)):
    return crud.create_course(db, data)


@router.post(
    "/students/{student_id}/grades",
    response_model=schemas.GradeOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Role.admin, Role.teacher))],
)
def add_grade(
    student_id: int,
    data: schemas.GradeCreate,
    db: Session = Depends(get_db),
):
    """Ajoute ou met à jour la note d'un étudiant (admin ou enseignant)."""
    if crud.get_student(db, student_id) is None:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    if crud.get_course(db, data.course_id) is None:
        raise HTTPException(status_code=404, detail="Cours introuvable")
    return crud.upsert_grade(db, student_id, data)
