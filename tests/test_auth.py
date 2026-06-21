"""Tests d'authentification et de contrôle d'accès par rôle."""


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_login_success(client):
    res = client.post(
        "/api/auth/login",
        data={"username": "admin@ecole.ma", "password": "admin1234"},
    )
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"


def test_login_wrong_password(client):
    res = client.post(
        "/api/auth/login",
        data={"username": "admin@ecole.ma", "password": "wrong"},
    )
    assert res.status_code == 401


def test_protected_route_requires_token(client):
    res = client.get("/api/students")
    assert res.status_code == 401


def test_student_role_cannot_list_students(client, admin_headers):
    # L'admin crée un compte étudiant.
    client.post(
        "/api/auth/users",
        headers=admin_headers,
        json={
            "email": "etudiant@ecole.ma",
            "full_name": "Etudiant Test",
            "password": "secret123",
            "role": "student",
        },
    )
    token = client.post(
        "/api/auth/login",
        data={"username": "etudiant@ecole.ma", "password": "secret123"},
    ).json()["access_token"]
    res = client.get(
        "/api/students", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403
