from fastapi.testclient import TestClient
from app.main import app
import io, openpyxl

client = TestClient(app)

def _token():
    # Registra un usuario y devuelve un token de autenticación
    client.post("/auth/register", json={
        "email": "u@mail.com", "name": "U", "password": "123456"
    })
    r = client.post(
        "/auth/login",
        data={"username": "u@mail.com", "password": "123456"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    return r.json()["access_token"]

def test_upload_excel_extracts_code():
    # Crear un archivo Excel en memoria con un código de ejemplo
    wb = openpyxl.Workbook()
    ws = wb.active
    ws["A1"] = "ACAP1234"
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)

    # Subir el archivo Excel al endpoint con un token válido
    token = _token()
    files = {"file": ("demo.xlsx", buf.getvalue(),
       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    r = client.post("/upload", files=files, headers={"Authorization": f"Bearer {token}"})

    # Validar que el código fue extraído correctamente
    assert r.status_code == 200
    assert r.json()["extracted"] == "ACAP1234"
