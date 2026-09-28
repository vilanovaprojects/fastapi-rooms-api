from app.models.sala import Sala
from app.repositories.sala_repository import SalaRepository
from app.schemas.sala_schema import SalaCreate
from tests.conftest import TestingSessionLocal, engine


def test_repository_crear_y_buscar():
    session = TestingSessionLocal()
    repo = SalaRepository(session)
    sala = repo.crear(
        SalaCreate(
            nombre="Laboratorio A",
            piso=2,
            capacidad=20,
            tipo_sala="Laboratorio",
        )
    )

    encontrado = repo.obtener_por_id(sala.id)
    assert encontrado is not None
    assert encontrado.nombre == "Laboratorio A"
    session.close()
