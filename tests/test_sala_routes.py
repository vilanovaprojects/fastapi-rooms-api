from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "mensaje" in response.json()


def test_get_salas_returns_200():
    response = client.get("/api/v1/salas")
    assert response.status_code == 200
    assert "salas" in response.json()


def test_create_sala_returns_201():
    payload = {
        "nombre": "Aula Nueva",
        "piso": 3,
        "capacidad": 40,
        "tipo_sala": "Aula",
        "numero_ventanas": 5,
        "tiene_proyector": True,
        "tiene_aire_acondicionado": False,
        "estado": "activa",
        "descripcion": "Nueva aula",
    }
    response = client.post("/api/v1/salas", json=payload)
    assert response.status_code == 201
    assert response.json()["nombre"] == "Aula Nueva"
