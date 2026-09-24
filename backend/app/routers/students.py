"""Endpoints de registro de contato com alunos."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.models import ContactLog, Student, User
from app.schemas.schemas import ContactLogCreate, ContactLogOut

router = APIRouter(prefix="/api/students", tags=["students"])


@router.post(
    "/{student_id}/contact-logs",
    response_model=ContactLogOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registra um contato com o aluno",
    description="Cria um registro de tentativa de contato (sem_resposta, retornou ou desistiu).",
)
def create_contact_log(
    student_id: int,
    payload: ContactLogCreate,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> ContactLogOut:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aluno não encontrado")

    log = ContactLog(
        student_id=student_id,
        course_id=payload.course_id,
        outcome=payload.outcome,
        notes=payload.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return ContactLogOut.model_validate(log)


@router.get(
    "/{student_id}/contact-logs",
    response_model=list[ContactLogOut],
    summary="Histórico de contatos de um aluno",
    description="Lista todos os registros de contato de um aluno, mais recentes primeiro.",
)
def list_contact_logs(
    student_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[ContactLogOut]:
    logs = (
        db.query(ContactLog)
        .filter(ContactLog.student_id == student_id)
        .order_by(ContactLog.contacted_at.desc())
        .all()
    )
    return [ContactLogOut.model_validate(item) for item in logs]
