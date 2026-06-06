"""Tests CRUD des étudiants."""


def _create_student(client, admin_headers, number="E001"):
    return client.post(
        "/api/students",
        headers=admin_headers,
        json={
            "first_name": "Amina",
            "last_name": "Benali",
            "student_number": number,
            "email": f"{number.lower()}@ecole.ma",
            "program": "Génie Logiciel",
        },
    )


def test_create_and_list_student(client, admin_headers):
    res = _create_student(client, admin_headers)
    assert res.status_code == 201
    student = res.json()
    assert student["student_number"] == "E001"

    res = client.get("/api/students", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_duplicate_student_number_rejected(client, admin_headers):
    _create_student(client, admin_headers, number="E010")
    res = _create_student(client, admin_headers, number="E010")
    assert res.status_code == 409


def test_update_student(client, admin_headers):
    sid = _create_student(client, admin_headers, number="E020").json()["id"]
    res = client.put(
        f"/api/students/{sid}",
        headers=admin_headers,
        json={"program": "Cybersécurité"},
    )
    assert res.status_code == 200
    assert res.json()["program"] == "Cybersécurité"


def test_delete_student(client, admin_headers):
    sid = _create_student(client, admin_headers, number="E030").json()["id"]
    res = client.delete(f"/api/students/{sid}", headers=admin_headers)
    assert res.status_code == 204
    res = client.get(f"/api/students/{sid}", headers=admin_headers)
    assert res.status_code == 404


def test_get_missing_student(client, admin_headers):
    res = client.get("/api/students/999", headers=admin_headers)
    assert res.status_code == 404
