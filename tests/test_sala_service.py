import pytest
from sqlalchemy.orm import Session

from app.models.sala import Base
from app.schemas.sala_schema import SalaCreate, SalaUpdate
from app.services.sala_service import SalaService
from tests.conftest import TestingSessionLocal, engine


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sala_service(db: Session):
    return SalaService(db)


def test_crear_sala_exitosamente(sala_service):
    sala_data = SalaCreate(
        nombre="Aula de Prueba",
        piso=2,
        capacidad=30,
        tipo_sala="Aula",
        numero_ventanas=4,
        tiene_proyector=True,
        tiene_aire_acondicionado=False,
        descripcion="Aula nueva",
    )

    sala = sala_service.crear_sala(sala_data)

    assert sala.id is not None
    assert sala.nombre == "Aula de Prueba"
    assert sala.piso == 2


def test_crear_sala_con_nombre_duplicado(sala_service):
    sala_data = SalaCreate(
        nombre="Aula Duplicada",
        piso=1,
        capacidad=25,
        tipo_sala="Aula",
    )
    sala_service.crear_sala(sala_data)

    try:
        sala_service.crear_sala(sala_data)
        assert False, "Se esperaba un conflicto"
    except Exception as exc:
        assert "ya existe" in str(exc)


def test_obtener_sala_por_id_inexistente(sala_service):
    try:
        sala_service.obtener_sala_por_id(999)
        assert False, "Se esperaba 404"
    except Exception as exc:
        assert "no encontrada" in str(exc)


def test_actualizar_sala_exitosamente(sala_service):
    sala = sala_service.crear_sala(
        SalaCreate(
            nombre="Aula Original",
            piso=1,
            capacidad=20,
            tipo_sala="Aula",
        )
    )

    actualizada = sala_service.actualizar_sala(sala.id, SalaUpdate(capacidad=30, tiene_proyector=True))

    assert actualizada.capacidad == 30
    assert actualizada.tiene_proyector is True


def test_eliminar_sala_exitosamente(sala_service):
    sala = sala_service.crear_sala(
        SalaCreate(
            nombre="Aula a Eliminar",
            piso=1,
            capacidad=20,
            tipo_sala="Aula",
        )
    )

    resultado = sala_service.eliminar_sala(sala.id)
    assert resultado is True
