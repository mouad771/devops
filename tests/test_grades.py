"""Tests de gestion des notes et d'export des relevés."""


def _setup_student_with_grades(client, admin_headers):
    student_id = client.post(
        "/api/students",
        headers=admin_headers,
        json={
            "first_name": "Yassine",
            "last_name": "Idrissi",
            "student_number": "E100",
            "email": "e100@ecole.ma",
            "program": "Data",
        },
    ).json()["id"]

    c1 = client.post(
        "/api/courses",
        headers=admin_headers,
        json={"code": "MATH1", "name": "Mathématiques", "credits": 4},
    ).json()["id"]
    c2 = client.post(
        "/api/courses",
        headers=admin_headers,
        json={"code": "INFO1", "name": "Algorithmique", "credits": 2},
    ).json()["id"]

    client.post(
        f"/api/students/{student_id}/grades",
        headers=admin_headers,
        json={"course_id": c1, "value": 15.0},
    )
    client.post(
        f"/api/students/{student_id}/grades",
        headers=admin_headers,
        json={"course_id": c2, "value": 12.0},
    )
    return student_id


def test_transcript_average_is_weighted(client, admin_headers):
    sid = _setup_student_with_grades(client, admin_headers)
    res = client.get(f"/api/students/{sid}/transcript", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data["lines"]) == 2
    # (15*4 + 12*2) / (4+2) = 84 / 6 = 14.0
    assert data["average"] == 14.0


def test_grade_upsert_updates_existing(client, admin_headers):
    sid = _setup_student_with_grades(client, admin_headers)
    course_id = client.get("/api/courses", headers=admin_headers).json()[0]["id"]
    client.post(
        f"/api/students/{sid}/grades",
        headers=admin_headers,
        json={"course_id": course_id, "value": 20.0},
    )
    res = client.get(f"/api/students/{sid}/transcript", headers=admin_headers)
    values = {line["course_code"]: line["value"] for line in res.json()["lines"]}
    assert values["MATH1"] == 20.0


def test_transcript_csv_export(client, admin_headers):
    sid = _setup_student_with_grades(client, admin_headers)
    res = client.get(f"/api/students/{sid}/transcript.csv", headers=admin_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    assert "Moyenne" in res.text


def test_transcript_pdf_export(client, admin_headers):
    sid = _setup_student_with_grades(client, admin_headers)
    res = client.get(f"/api/students/{sid}/transcript.pdf", headers=admin_headers)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content[:4] == b"%PDF"


def test_grade_for_missing_student(client, admin_headers):
    res = client.post(
        "/api/students/999/grades",
        headers=admin_headers,
        json={"course_id": 1, "value": 10.0},
    )
    assert res.status_code == 404
