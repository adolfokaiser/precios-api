from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_login_profile():
    r = client.post("/auth/register", json={
        "email": "test@mail.com", "name": "Test", "password": "123456"
    })
    assert r.status_code in (201, 400)  # 400 si ya existía

    r = client.post(
        "/auth/login",
        data={"username": "test@mail.com", "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = client.get("/profile", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "test@mail.com"
