"""Endpoints de relatórios: funil, score de risco e comparação entre turmas."""

import csv
import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.models import Course, User
from app.schemas.schemas import ComparisonItem, FunnelReport, RiskScoreItem
from app.services.reports import build_funnel_report, build_risk_score_items

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get(
    "/funnel",
    response_model=FunnelReport,
    summary="Funil de matrícula até conclusão",
    description="Retorna contagens por etapa (matriculados, ativos, em risco, "
    "desistentes, concluintes) e a taxa de evasão. Filtra por curso quando informado.",
)
def get_funnel(
    course_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> FunnelReport:
    return build_funnel_report(db, course_id=course_id)


@router.get(
    "/risk-score",
    response_model=list[RiskScoreItem],
    summary="Lista de alunos ordenada por score de risco",
    description="Retorna matrículas ativas ordenadas por score de risco decrescente. "
    "Filtra por curso e/ou faixa de risco (baixo, medio, alto).",
)
def get_risk_score(
    course_id: int | None = Query(default=None),
    level: str | None = Query(default=None, pattern="^(baixo|medio|alto)$"),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[RiskScoreItem]:
    return build_risk_score_items(db, course_id=course_id, level=level)


@router.get(
    "/comparison",
    response_model=list[ComparisonItem],
    summary="Compara o funil entre várias turmas",
    description="Recebe uma lista de IDs de curso separados por vírgula "
    "(ex.: course_ids=1,2,3) e retorna o funil de cada uma.",
)
def get_comparison(
    course_ids: str = Query(..., description="IDs separados por vírgula, ex.: 1,2,3"),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> list[ComparisonItem]:
    ids = [int(x) for x in course_ids.split(",") if x.strip()]
    items = []
    for course_id in ids:
        course = db.get(Course, course_id)
        if course is None:
            continue
        funnel = build_funnel_report(db, course_id=course_id)
        items.append(ComparisonItem(course_id=course_id, course_name=course.name, funnel=funnel))
    return items


@router.get(
    "/risk-score/export",
    summary="Exporta a lista de risco em CSV",
    description="Mesmo conteúdo de /reports/risk-score, em formato CSV para download.",
)
def export_risk_score(
    course_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
) -> StreamingResponse:
    items = build_risk_score_items(db, course_id=course_id)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "enrollment_id",
            "student_id",
            "student_name",
            "course_id",
            "course_name",
            "days_inactive",
            "submission_rate",
            "score",
            "level",
        ]
    )
    for item in items:
        writer.writerow(
            [
                item.enrollment_id,
                item.student_id,
                item.student_name,
                item.course_id,
                item.course_name,
                item.days_inactive,
                item.submission_rate,
                item.score,
                item.level.value,
            ]
        )
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=risco_evasao.csv"},
    )
