"""Script idempotente de seed: cria usuário demo, cursos, alunos, atividades,
entregas e alguns contatos já registrados. Datas relativas à data atual.

Uso:
    python -m scripts.seed
"""

from __future__ import annotations

import json
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

from sqlalchemy import inspect

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.models.models import (
    Activity,
    ContactLog,
    ContactOutcome,
    Course,
    Enrollment,
    EnrollmentStatus,
    Student,
    Submission,
    User,
)

random.seed(42)

COURSES = [
    {"name": "Introdução à Programação", "category": "Tecnologia"},
    {"name": "Gestão de Projetos", "category": "Negócios"},
    {"name": "Libras Básico", "category": "Educação Inclusiva"},
]

ACTIVITIES_PER_COURSE = 6
STUDENTS_PER_COURSE = 100


def get_or_create_demo_user(db) -> None:
    existing = db.query(User).filter(User.email == settings.demo_user_email).first()
    if existing:
        return
    db.add(
        User(
            name="Usuário Demo",
            email=settings.demo_user_email,
            hashed_password=hash_password(settings.demo_user_password),
        )
    )


def get_or_create_courses(db) -> list[Course]:
    courses = []
    for data in COURSES:
        course = db.query(Course).filter(Course.name == data["name"]).first()
        if not course:
            course = Course(name=data["name"], category=data["category"])
            db.add(course)
            db.flush()
        courses.append(course)
    return courses


def get_or_create_activities(db, course: Course) -> list[Activity]:
    existing = db.query(Activity).filter(Activity.course_id == course.id).all()
    if existing:
        return existing
    activities = []
    for i in range(1, ACTIVITIES_PER_COURSE + 1):
        activity = Activity(course_id=course.id, title=f"Atividade {i}", weight=1)
        db.add(activity)
        db.flush()
        activities.append(activity)
    return activities


def build_profile() -> dict:
    """Sorteia um perfil de engajamento do aluno."""
    roll = random.random()
    if roll < 0.35:
        return {
            "status": EnrollmentStatus.ATIVO,
            "inactivity_days": random.randint(0, 5),
            "rate": random.uniform(0.7, 1.0),
        }
    if roll < 0.6:
        return {
            "status": EnrollmentStatus.ATIVO,
            "inactivity_days": random.randint(10, 25),
            "rate": random.uniform(0.3, 0.7),
        }
    if roll < 0.8:
        return {
            "status": EnrollmentStatus.ATIVO,
            "inactivity_days": random.randint(25, 60),
            "rate": random.uniform(0.0, 0.3),
        }
    if roll < 0.92:
        return {
            "status": EnrollmentStatus.DESISTENTE,
            "inactivity_days": random.randint(30, 90),
            "rate": random.uniform(0.0, 0.4),
        }
    return {
        "status": EnrollmentStatus.CONCLUIDO,
        "inactivity_days": random.randint(0, 10),
        "rate": 1.0,
    }


def seed_course_students(db, course: Course, activities: list[Activity], start_index: int) -> int:
    now = datetime.now(UTC)
    new_count = 0

    for i in range(STUDENTS_PER_COURSE):
        idx = start_index + i
        email = f"aluno{idx}@exemplo.com"
        student = db.query(Student).filter(Student.email == email).first()
        if not student:
            student = Student(name=f"Aluno {idx}", email=email, phone=f"+55119{idx:08d}"[:15])
            db.add(student)
            db.flush()

        existing_enrollment = (
            db.query(Enrollment)
            .filter(Enrollment.student_id == student.id, Enrollment.course_id == course.id)
            .first()
        )
        if existing_enrollment:
            continue

        profile = build_profile()
        enrolled_at = now - timedelta(days=random.randint(60, 180))
        last_access_at = now - timedelta(days=profile["inactivity_days"])
        completed_at = (
            now - timedelta(days=random.randint(0, 5))
            if profile["status"] == EnrollmentStatus.CONCLUIDO
            else None
        )

        enrollment = Enrollment(
            student_id=student.id,
            course_id=course.id,
            status=profile["status"],
            enrolled_at=enrolled_at,
            last_access_at=last_access_at,
            completed_at=completed_at,
        )
        db.add(enrollment)
        db.flush()

        n_submitted = round(len(activities) * profile["rate"])
        for activity in activities[:n_submitted]:
            db.add(
                Submission(
                    enrollment_id=enrollment.id,
                    activity_id=activity.id,
                    submitted_at=enrolled_at + timedelta(days=random.randint(1, 40)),
                )
            )

        if profile["status"] == EnrollmentStatus.DESISTENTE and random.random() < 0.4:
            db.add(
                ContactLog(
                    student_id=student.id,
                    course_id=course.id,
                    contacted_at=now - timedelta(days=random.randint(1, 20)),
                    outcome=random.choice(list(ContactOutcome)),
                    notes="Contato registrado automaticamente pelo seed.",
                )
            )

        new_count += 1

    return new_count


def export_demo_data(payload: dict) -> None:
    demo_dir = Path(__file__).resolve().parents[2] / "frontend" / "src" / "demo-data"
    demo_dir.mkdir(parents=True, exist_ok=True)
    (demo_dir / "seed.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def build_export_payload(db, courses: list[Course]) -> dict:
    """Monta o payload exportado a partir do estado atual do banco (não
    apenas dos registros criados nesta execução), para que o export seja
    correto mesmo em execuções idempotentes que não criam nada de novo."""
    activities_by_course: dict[int, list[Activity]] = {
        course.id: db.query(Activity).filter(Activity.course_id == course.id).all()
        for course in courses
    }
    all_activities = [
        {"id": a.id, "course_id": a.course_id, "title": a.title, "weight": a.weight}
        for activities in activities_by_course.values()
        for a in activities
    ]

    enrollments = (
        db.query(Enrollment).filter(Enrollment.course_id.in_([c.id for c in courses])).all()
    )
    records = []
    for enrollment in enrollments:
        activities = activities_by_course.get(enrollment.course_id, [])
        n_submitted = db.query(Submission).filter(Submission.enrollment_id == enrollment.id).count()
        submission_rate = min(n_submitted / len(activities), 1.0) if activities else 1.0
        records.append(
            {
                "student": {
                    "id": enrollment.student.id,
                    "name": enrollment.student.name,
                    "email": enrollment.student.email,
                },
                "enrollment": {
                    "id": enrollment.id,
                    "course_id": enrollment.course_id,
                    "status": enrollment.status.value,
                    "enrolled_at": enrollment.enrolled_at.isoformat(),
                    "last_access_at": (
                        enrollment.last_access_at.isoformat() if enrollment.last_access_at else None
                    ),
                    "completed_at": (
                        enrollment.completed_at.isoformat() if enrollment.completed_at else None
                    ),
                },
                "submission_rate": round(submission_rate, 4),
            }
        )

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "courses": [{"id": c.id, "name": c.name, "category": c.category} for c in courses],
        "activities": all_activities,
        "enrollments": records,
    }


def main() -> None:
    if not inspect(engine).has_table("users"):
        raise RuntimeError(
            "As tabelas do banco ainda não existem. Rode 'alembic upgrade head' "
            "antes de executar o seed."
        )

    db = SessionLocal()
    try:
        get_or_create_demo_user(db)
        courses = get_or_create_courses(db)
        db.flush()

        new_count = 0
        for i, course in enumerate(courses):
            activities = get_or_create_activities(db, course)
            new_count += seed_course_students(
                db, course, activities, start_index=i * STUDENTS_PER_COURSE + 1
            )

        db.commit()

        payload = build_export_payload(db, courses)
        export_demo_data(payload)
        print(
            f"Seed concluído: {len(courses)} cursos, {new_count} matrículas novas processadas, "
            f"{len(payload['enrollments'])} matrículas exportadas no total."
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
