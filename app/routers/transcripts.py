"""Routes d'export des relevés de notes (JSON, CSV, PDF)."""

import csv
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse
from fpdf import FPDF
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.models import Role, User
from app.security import get_current_user

router = APIRouter(prefix="/api/students", tags=["transcripts"])


def _authorize_transcript(student, current_user: User) -> None:
    """Un étudiant ne peut consulter que son propre relevé."""
    if current_user.role in (Role.admin, Role.teacher):
        return
    if student.user_id == current_user.id:
        return
    raise HTTPException(status_code=403, detail="Accès refusé à ce relevé")


def _load_transcript(student_id: int, db: Session, current_user: User):
    student = crud.get_student(db, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Étudiant introuvable")
    _authorize_transcript(student, current_user)
    return crud.get_transcript(db, student)


@router.get("/{student_id}/transcript", response_model=schemas.Transcript)
def get_transcript(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.Transcript:
    return _load_transcript(student_id, db, current_user)


@router.get("/{student_id}/transcript.csv")
def get_transcript_csv(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    transcript = _load_transcript(student_id, db, current_user)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Code", "Cours", "Crédits", "Note /20"])
    for line in transcript.lines:
        writer.writerow(
            [line.course_code, line.course_name, line.credits, line.value]
        )
    writer.writerow([])
    writer.writerow(["Moyenne pondérée", "", "", transcript.average])
    buffer.seek(0)
    filename = f"releve_{transcript.student.student_number}.csv"
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/{student_id}/transcript.pdf")
def get_transcript_pdf(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    transcript = _load_transcript(student_id, db, current_user)
    student = transcript.student

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Releve de notes", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Etudiant : {student.first_name} {student.last_name}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Numero : {student.student_number}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, f"Filiere : {student.program or '-'}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(30, 8, "Code", border=1)
    pdf.cell(90, 8, "Cours", border=1)
    pdf.cell(25, 8, "Credits", border=1, align="C")
    pdf.cell(30, 8, "Note /20", border=1, align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    for line in transcript.lines:
        pdf.cell(30, 8, line.course_code, border=1)
        pdf.cell(90, 8, line.course_name[:45], border=1)
        pdf.cell(25, 8, str(line.credits), border=1, align="C")
        pdf.cell(30, 8, f"{line.value:.2f}", border=1, align="C",
                 new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    avg = "-" if transcript.average is None else f"{transcript.average:.2f} / 20"
    pdf.cell(0, 8, f"Moyenne ponderee : {avg}",
             new_x="LMARGIN", new_y="NEXT")

    content = bytes(pdf.output())
    filename = f"releve_{student.student_number}.pdf"
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
