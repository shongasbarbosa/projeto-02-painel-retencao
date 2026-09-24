"""Endpoints de cursos."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.models import Course, User
from app.schemas.schemas import CourseOut

router = APIRouter(prefix="/api/courses", tags=["courses"])


@router.get(
    "",
    response_model=list[CourseOut],
    summary="Lista os cursos cadastrados",
    description="Retorna todos os cursos, incluindo sua categoria.",
)
def list_courses(
    db: Session = Depends(get_db), _user: User = Depends(get_current_user)
) -> list[CourseOut]:
    courses = db.query(Course).order_by(Course.name).all()
    return [CourseOut.model_validate(c) for c in courses]
