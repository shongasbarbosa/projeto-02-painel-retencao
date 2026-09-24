"""Testes de autenticação e de permissões dos endpoints protegidos."""


def test_login_with_valid_credentials_returns_token(client, demo_user):
    response = client.post(
        "/api/auth/login", json={"email": demo_user.email, "password": "demo123456"}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_with_invalid_password_is_rejected(client, demo_user):
    response = client.post(
        "/api/auth/login", json={"email": demo_user.email, "password": "senha-errada"}
    )
    assert response.status_code == 401


def test_login_with_unknown_email_is_rejected(client):
    response = client.post(
        "/api/auth/login", json={"email": "ninguem@exemplo.com", "password": "qualquer"}
    )
    assert response.status_code == 401


def test_protected_endpoint_requires_token(client):
    response = client.get("/api/courses")
    assert response.status_code == 401


def test_protected_endpoint_rejects_invalid_token(client):
    response = client.get("/api/courses", headers={"Authorization": "Bearer token-invalido"})
    assert response.status_code == 401


def test_protected_endpoint_accepts_valid_token(client, auth_headers):
    response = client.get("/api/courses", headers=auth_headers)
    assert response.status_code == 200


def test_health_endpoint_is_public(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
