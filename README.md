# FastAPI Rooms API

API REST para gestionar salas educativas, construida con FastAPI, SQLAlchemy y un patrón Repository-Service.

## Tecnologías
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite (desarrollo)
- Pytest

## Estructura del proyecto

```text
app/
├── __init__.py
├── config.py
├── main.py
├── models/
│   ├── __init__.py
│   └── sala.py
├── schemas/
│   ├── __init__.py
│   └── sala_schema.py
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py
│   └── sala_repository.py
├── services/
│   ├── __init__.py
│   └── sala_service.py
├── routes/
│   ├── __init__.py
│   └── sala_routes.py
tests/
├── __init__.py
├── conftest.py
├── test_sala_service.py
├── test_sala_repository.py
└── test_sala_routes.py
```

## Requisitos

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar la API

```bash
uvicorn app.main:app --reload
```

La documentación Swagger estará disponible en:
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Endpoints principales

- GET `/api/v1/salas`
- GET `/api/v1/salas/{sala_id}`
- POST `/api/v1/salas`
- PUT `/api/v1/salas/{sala_id}`
- DELETE `/api/v1/salas/{sala_id}`

## Ejecutar tests

```bash
pytest -v
```

## Base de datos

La aplicación usa SQLite por defecto para evitar configuración adicional en desarrollo:

```python
sqlite:///./test.db
```

## Estado

Proyecto base de ejemplo para práctica académica y aprendizaje de arquitectura backend con FastAPI.
