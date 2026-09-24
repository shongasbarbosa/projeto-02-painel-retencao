"""Testes de matrículas e registro de contatos."""

from app.models.models import Course, Student


def _make_course(db_session):
    course = Course(name="Curso Teste", category="Tecnologia")
    db_session.add(course)
    db_session.flush()
    db_session.commit()
    return course


def _make_student(db_session):
    student = Student(name="Aluno Teste", email="aluno.teste@exemplo.com")
    db_session.add(student)
    db_session.flush()
    db_session.commit()
    return student


def test_create_enrollment(client, auth_headers, db_session):
    course = _make_course(db_session)
    student = _make_student(db_session)

    response = client.post(
        "/api/enrollments",
        json={"student_id": student.id, "course_id": course.id},
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "ativo"
    assert body["student_id"] == student.id


def test_update_enrollment_status(client, auth_headers, db_session):
    course = _make_course(db_session)
    student = _make_student(db_session)
    created = client.post(
        "/api/enrollments",
        json={"student_id": student.id, "course_id": course.id},
        headers=auth_headers,
    ).json()

    response = client.patch(
        f"/api/enrollments/{created['id']}/status",
        json={"status": "desistente"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "desistente"


def test_update_enrollment_status_not_found(client, auth_headers):
    response = client.patch(
        "/api/enrollments/999999/status", json={"status": "ativo"}, headers=auth_headers
    )
    assert response.status_code == 404


def test_create_and_list_contact_logs(client, auth_headers, db_session):
    course = _make_course(db_session)
    student = _make_student(db_session)

    create_response = client.post(
        f"/api/students/{student.id}/contact-logs",
        json={"course_id": course.id, "outcome": "sem_resposta", "notes": "Primeira tentativa"},
        headers=auth_headers,
    )
    assert create_response.status_code == 201

    list_response = client.get(f"/api/students/{student.id}/contact-logs", headers=auth_headers)
    assert list_response.status_code == 200
    logs = list_response.json()
    assert len(logs) == 1
    assert logs[0]["outcome"] == "sem_resposta"


def test_contact_log_for_unknown_student_returns_404(client, auth_headers, db_session):
    course = _make_course(db_session)
    response = client.post(
        "/api/students/999999/contact-logs",
        json={"course_id": course.id, "outcome": "retornou"},
        headers=auth_headers,
    )
    assert response.status_code == 404
