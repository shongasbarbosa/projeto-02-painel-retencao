"""Consultas e cálculos usados nos relatórios do painel."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.models import Activity, Enrollment, EnrollmentStatus, Submission
from app.schemas.schemas import FunnelReport, RiskScoreItem
from app.services.risk_score import calculate_risk_score, classify_risk


def _submission_rate(db: Session, enrollment: Enrollment) -> float:
    total_activities = (
        db.query(func.count(Activity.id))
        .filter(Activity.course_id == enrollment.course_id)
        .scalar()
        or 0
    )
    if total_activities == 0:
        return 1.0
    submitted = (
        db.query(func.count(Submission.id))
        .filter(Submission.enrollment_id == enrollment.id)
        .scalar()
        or 0
    )
    return min(submitted / total_activities, 1.0)


def _days_inactive(enrollment: Enrollment, reference: datetime) -> int:
    last_moment = enrollment.last_access_at or enrollment.enrolled_at
    delta = reference - last_moment
    return max(delta.days, 0)


def build_risk_score_items(
    db: Session, course_id: int | None = None, level: str | None = None
) -> list[RiskScoreItem]:
    query = db.query(Enrollment).filter(Enrollment.status == EnrollmentStatus.ATIVO)
    if course_id is not None:
        query = query.filter(Enrollment.course_id == course_id)

    reference = datetime.now(UTC)
    items: list[RiskScoreItem] = []
    for enrollment in query.all():
        days_inactive = _days_inactive(enrollment, reference)
        submission_rate = _submission_rate(db, enrollment)
        score = calculate_risk_score(days_inactive, submission_rate)
        risk_level = classify_risk(score)
        if level is not None and risk_level.value != level:
            continue
        items.append(
            RiskScoreItem(
                enrollment_id=enrollment.id,
                student_id=enrollment.student_id,
                student_name=enrollment.student.name,
                course_id=enrollment.course_id,
                course_name=enrollment.course.name,
                days_inactive=days_inactive,
                submission_rate=round(submission_rate, 4),
                score=score,
                level=risk_level,
            )
        )
    items.sort(key=lambda item: item.score, reverse=True)
    return items


def build_funnel_report(db: Session, course_id: int | None = None) -> FunnelReport:
    query = db.query(Enrollment)
    if course_id is not None:
        query = query.filter(Enrollment.course_id == course_id)
    enrollments = query.all()

    matriculados = len(enrollments)
    ativos = sum(1 for e in enrollments if e.status == EnrollmentStatus.ATIVO)
    desistentes = sum(1 for e in enrollments if e.status == EnrollmentStatus.DESISTENTE)
    concluintes = sum(1 for e in enrollments if e.status == EnrollmentStatus.CONCLUIDO)

    em_risco = 0
    if course_id is not None:
        em_risco = sum(
            1 for item in build_risk_score_items(db, course_id=course_id) if item.level != "baixo"
        )
    else:
        em_risco = sum(1 for item in build_risk_score_items(db) if item.level != "baixo")

    taxa_evasao = round(desistentes / matriculados, 4) if matriculados else 0.0

    return FunnelReport(
        matriculados=matriculados,
        ativos=ativos,
        em_risco=em_risco,
        desistentes=desistentes,
        concluintes=concluintes,
        taxa_evasao=taxa_evasao,
    )
