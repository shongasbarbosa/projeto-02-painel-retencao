"""Endpoints de matrículas."""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.models import Enrollment, User
from app.schemas.schemas import EnrollmentCreate, EnrollmentOut, EnrollmentStatusUpdate

router = APIRouter(prefix="/api/enrollments", tags=["enrollments"])


@router.post(
    "",
    response_model=EnrollmentOut,
    status_code=status.HTTP_201_CREATED,
    summary="Cria uma matrícula",
    description="Matricula um aluno em um curso, com status inicial 'ativo'.",
)
def create_enrollment(
    payload: EnrollmentCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> EnrollmentOut:
    enrollment = Enrollment(
        student_id=payload.student_id,
        course_id=payload.course_id,
        enrolled_at=payload.enrolled_at or datetime.now(UTC),
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return EnrollmentOut.model_validate(enrollment)


@router.patch(
    "/{enrollment_id}/status",
    response_model=EnrollmentOut,
    summary="Atualiza o status de uma matrícula",
    description="Altera o status para ativo, desistente ou concluido.",
)
def update_enrollment_status(
    enrollment_id: int,
    payload: EnrollmentStatusUpdate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> EnrollmentOut:
    enrollment = db.get(Enrollment, enrollment_id)
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Matrícula não encontrada"
        )

    enrollment.status = payload.status
    if payload.status.value == "concluido":
        enrollment.completed_at = datetime.now(UTC)
    db.commit()
    db.refresh(enrollment)
    return EnrollmentOut.model_validate(enrollment)
