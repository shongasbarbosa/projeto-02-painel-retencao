"""Testes dos relatórios de funil, score de risco e comparação entre turmas."""

from datetime import UTC, datetime, timedelta

from app.models.models import Activity, Course, Enrollment, EnrollmentStatus, Student, Submission


def _make_course(db_session, name="Curso A", category="Tecnologia"):
    course = Course(name=name, category=category)
    db_session.add(course)
    db_session.flush()
    return course


def _make_student(db_session, email, name="Aluno Teste"):
    student = Student(name=name, email=email)
    db_session.add(student)
    db_session.flush()
    return student


def _make_activity(db_session, course, title="Atividade 1"):
    activity = Activity(course_id=course.id, title=title, weight=1)
    db_session.add(activity)
    db_session.flush()
    return activity


def test_funnel_counts_by_status(db_session, client, auth_headers):
    course = _make_course(db_session)
    now = datetime.now(UTC)

    statuses = [
        EnrollmentStatus.ATIVO,
        EnrollmentStatus.ATIVO,
        EnrollmentStatus.DESISTENTE,
        EnrollmentStatus.CONCLUIDO,
    ]
    for i, status in enumerate(statuses):
        student = _make_student(db_session, f"aluno{i}@teste.com")
        db_session.add(
            Enrollment(
                student_id=student.id,
                course_id=course.id,
                status=status,
                enrolled_at=now - timedelta(days=10),
                last_access_at=now - timedelta(days=1),
            )
        )
    db_session.commit()

    response = client.get(f"/api/reports/funnel?course_id={course.id}", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["matriculados"] == 4
    assert body["ativos"] == 2
    assert body["desistentes"] == 1
    assert body["concluintes"] == 1
    assert body["taxa_evasao"] == 0.25


def test_risk_score_orders_by_score_descending(db_session, client, auth_headers):
    course = _make_course(db_session)
    activity = _make_activity(db_session, course)
    now = datetime.now(UTC)

    engaged = _make_student(db_session, "engajado@teste.com")
    disengaged = _make_student(db_session, "desengajado@teste.com")

    engaged_enrollment = Enrollment(
        student_id=engaged.id,
        course_id=course.id,
        status=EnrollmentStatus.ATIVO,
        enrolled_at=now - timedelta(days=20),
        last_access_at=now,
    )
    disengaged_enrollment = Enrollment(
        student_id=disengaged.id,
        course_id=course.id,
        status=EnrollmentStatus.ATIVO,
        enrolled_at=now - timedelta(days=60),
        last_access_at=now - timedelta(days=45),
    )
    db_session.add_all([engaged_enrollment, disengaged_enrollment])
    db_session.flush()

    db_session.add(
        Submission(enrollment_id=engaged_enrollment.id, activity_id=activity.id, submitted_at=now)
    )
    db_session.commit()

    response = client.get(f"/api/reports/risk-score?course_id={course.id}", headers=auth_headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 2
    assert items[0]["student_id"] == disengaged.id
    assert items[0]["level"] == "alto"
    assert items[1]["student_id"] == engaged.id
    assert items[0]["score"] >= items[1]["score"]


def test_comparison_returns_funnel_per_course(db_session, client, auth_headers):
    course_a = _make_course(db_session, name="Curso A")
    course_b = _make_course(db_session, name="Curso B")
    now = datetime.now(UTC)

    for course, n_active in [(course_a, 3), (course_b, 1)]:
        for i in range(n_active):
            student = _make_student(db_session, f"{course.name}-{i}@teste.com")
            db_session.add(
                Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    status=EnrollmentStatus.ATIVO,
                    enrolled_at=now - timedelta(days=5),
                    last_access_at=now,
                )
            )
    db_session.commit()

    response = client.get(
        f"/api/reports/comparison?course_ids={course_a.id},{course_b.id}", headers=auth_headers
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    by_id = {item["course_id"]: item for item in body}
    assert by_id[course_a.id]["funnel"]["matriculados"] == 3
    assert by_id[course_b.id]["funnel"]["matriculados"] == 1


def test_risk_score_export_returns_csv(db_session, client, auth_headers):
    course = _make_course(db_session)
    student = _make_student(db_session, "aluno@teste.com")
    now = datetime.now(UTC)
    db_session.add(
        Enrollment(
            student_id=student.id,
            course_id=course.id,
            status=EnrollmentStatus.ATIVO,
            enrolled_at=now - timedelta(days=40),
            last_access_at=now - timedelta(days=35),
        )
    )
    db_session.commit()

    response = client.get(
        f"/api/reports/risk-score/export?course_id={course.id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert "aluno@teste.com" not in response.text  # CSV usa nome, não e-mail
    assert "score" in response.text
