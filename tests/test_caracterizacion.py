"""
Tests de Caracterización - Verifican que el código mantiene su comportamiento.

Estos tests capturan el comportamiento actual antes de refactorizar,
y se ejecutan después para verificar que la refactorización no rompió nada.
"""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.models.sala import Base
from app.repositories.sala_repository import SalaRepository
from app.schemas.sala_schema import SalaCreate, SalaUpdate
from app.services.sala_service import SalaService
from tests.conftest import TestingSessionLocal, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_bd():
    """Limpia la base de datos antes de cada test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_test():
    """Sesión de BD para tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


class TestSalaRepositorio:
    """Tests de caracterización para SalaRepository."""

    def test_crear_persiste_sala_en_bd(self, db_test):
        """Verifica que crear() persiste la sala en BD."""
        repo = SalaRepository(db_test)
        datos = SalaCreate(
            nombre="Laboratorio A",
            piso=2,
            capacidad=20,
            tipo_sala="Laboratorio",
        )

        sala = repo.crear(datos)

        assert sala.id is not None
        assert sala.nombre == "Laboratorio A"

        # Verificar que está persistida
        sala_recuperada = repo.obtener_por_id(sala.id)
        assert sala_recuperada is not None
        assert sala_recuperada.nombre == "Laboratorio A"

    def test_obtener_por_nombre_encuentra_sala(self, db_test):
        """Verifica que obtener_por_nombre() encuentra salas correctamente."""
        repo = SalaRepository(db_test)
        repo.crear(SalaCreate(
            nombre="Única",
            piso=1,
            capacidad=30,
            tipo_sala="Aula",
        ))

        encontrada = repo.obtener_por_nombre("Única")

        assert encontrada is not None
        assert encontrada.nombre == "Única"

    def test_obtener_por_nombre_retorna_none_si_no_existe(self, db_test):
        """Verifica que obtener_por_nombre() devuelve None si no existe."""
        repo = SalaRepository(db_test)

        resultado = repo.obtener_por_nombre("Inexistente")

        assert resultado is None

    def test_filtrar_por_tipo_sala(self, db_test):
        """Verifica que filtrar() aplica correctamente el filtro tipo_sala."""
        repo = SalaRepository(db_test)
        repo.crear(SalaCreate(
            nombre="Aula 1",
            piso=1,
            capacidad=30,
            tipo_sala="Aula",
        ))
        repo.crear(SalaCreate(
            nombre="Lab 1",
            piso=2,
            capacidad=20,
            tipo_sala="Laboratorio",
        ))

        aulas = repo.filtrar(tipo_sala="Aula")

        assert len(aulas) == 1
        assert aulas[0].tipo_sala == "Aula"

    def test_filtrar_por_estado(self, db_test):
        """Verifica que filtrar() aplica correctamente el filtro estado."""
        repo = SalaRepository(db_test)
        repo.crear(SalaCreate(
            nombre="Activa",
            piso=1,
            capacidad=30,
            tipo_sala="Aula",
            estado="activa",
        ))
        repo.crear(SalaCreate(
            nombre="Mantenimiento",
            piso=2,
            capacidad=20,
            tipo_sala="Aula",
            estado="mantenimiento",
        ))

        activas = repo.filtrar(estado="activa")

        assert len(activas) == 1
        assert activas[0].estado == "activa"

    def test_actualizar_modifica_campos(self, db_test):
        """Verifica que actualizar() modifica los campos correctamente."""
        repo = SalaRepository(db_test)
        sala = repo.crear(SalaCreate(
            nombre="Aula A",
            piso=1,
            capacidad=30,
            tipo_sala="Aula",
        ))

        actualizada = repo.actualizar(sala.id, SalaUpdate(capacidad=50))

        assert actualizada.capacidad == 50
        assert actualizada.nombre == "Aula A"  # No cambió

    def test_actualizar_retorna_none_si_no_existe(self, db_test):
        """Verifica que actualizar() devuelve None si la sala no existe."""
        repo = SalaRepository(db_test)

        resultado = repo.actualizar(999, SalaUpdate(capacidad=50))

        assert resultado is None

    def test_eliminar_remueve_de_bd(self, db_test):
        """Verifica que eliminar() remueve la sala de BD."""
        repo = SalaRepository(db_test)
        sala = repo.crear(SalaCreate(
            nombre="Temporal",
            piso=1,
            capacidad=30,
            tipo_sala="Aula",
        ))

        fue_eliminada = repo.eliminar(sala.id)

        assert fue_eliminada is True
        recuperada = repo.obtener_por_id(sala.id)
        assert recuperada is None

    def test_eliminar_retorna_false_si_no_existe(self, db_test):
        """Verifica que eliminar() devuelve False si no existe."""
        repo = SalaRepository(db_test)

        resultado = repo.eliminar(999)

        assert resultado is False

    def test_contar_total_devuelve_cantidad_correcta(self, db_test):
        """Verifica que contar_total() devuelve la cantidad exacta."""
        repo = SalaRepository(db_test)
        repo.crear(SalaCreate(nombre="Aula 1", piso=1, capacidad=30, tipo_sala="Aula"))
        repo.crear(SalaCreate(nombre="Aula 2", piso=1, capacidad=30, tipo_sala="Aula"))

        total = repo.contar_total()

        assert total == 2


class TestSalaService:
    """Tests de caracterización para SalaService."""

    def test_crear_sala_valida_persiste(self, db_test):
        """Verifica que crear_sala() valida y persiste correctamente."""
        servicio = SalaService(db_test)
        datos = SalaCreate(
            nombre="Test",
            piso=1,
            capacidad=30,
            tipo_sala="Aula",
        )

        sala = servicio.crear_sala(datos)

        assert sala.id is not None
        assert sala.nombre == "Test"
        assert sala.piso == 1

    def test_crear_sala_rechaza_nombre_duplicado(self, db_test):
        """Verifica que crear_sala() rechaza nombres duplicados."""
        servicio = SalaService(db_test)
        datos = SalaCreate(
            nombre="Duplicado",
            piso=1,
            capacidad=30,
            tipo_sala="Aula",
        )
        servicio.crear_sala(datos)

        with pytest.raises(HTTPException) as exc_info:
            servicio.crear_sala(datos)

        assert exc_info.value.status_code == 409
        assert "ya existe" in exc_info.value.detail

    def test_obtener_todas_salas_pagina_correctamente(self, db_test):
        """Verifica que obtener_todas_salas() pagina correctamente."""
        servicio = SalaService(db_test)
        # Crear 15 salas
        for i in range(15):
            servicio.crear_sala(SalaCreate(
                nombre=f"Aula {i}",
                piso=1,
                capacidad=30,
                tipo_sala="Aula",
            ))

        resultado = servicio.obtener_todas_salas(skip=0, limit=10)

        assert resultado["total"] == 15
        assert len(resultado["salas"]) == 10
        assert resultado["skip"] == 0
        assert resultado["limit"] == 10

    def test_obtener_todas_salas_con_filtro_tipo(self, db_test):
        """Verifica que obtener_todas_salas() aplica filtro tipo_sala."""
        servicio = SalaService(db_test)
        servicio.crear_sala(SalaCreate(
            nombre="Aula 1",
            piso=1,
            capacidad=30,
            tipo_sala="Aula",
        ))
        servicio.crear_sala(SalaCreate(
            nombre="Lab 1",
            piso=2,
            capacidad=20,
            tipo_sala="Laboratorio",
        ))

        resultado = servicio.obtener_todas_salas(tipo_sala="Aula")

        assert resultado["total"] == 2  # Total general
        assert len(resultado["salas"]) == 1  # Solo aulas
        assert resultado["salas"][0].tipo_sala == "Aula"

    def test_obtener_sala_por_id_no_encontrada_lanza_404(self, db_test):
        """Verifica que obtener_sala_por_id() lanza 404 si no existe."""
        servicio = SalaService(db_test)

        with pytest.raises(HTTPException) as exc_info:
            servicio.obtener_sala_por_id(999)

        assert exc_info.value.status_code == 404
        assert "no encontrada" in exc_info.value.detail

    def test_actualizar_sala_valida_nombre_unico(self, db_test):
        """Verifica que actualizar_sala() valida nombres únicos."""
        servicio = SalaService(db_test)
        sala1 = servicio.crear_sala(SalaCreate(
            nombre="Aula 1",
            piso=1,
            capacidad=30,
            tipo_sala="Aula",
        ))
        sala2 = servicio.crear_sala(SalaCreate(
            nombre="Aula 2",
            piso=1,
            capacidad=30,
            tipo_sala="Aula",
        ))

        with pytest.raises(HTTPException) as exc_info:
            servicio.actualizar_sala(sala2.id, SalaUpdate(nombre="Aula 1"))

        assert exc_info.value.status_code == 409

    def test_actualizar_sala_permite_mismo_nombre(self, db_test):
        """Verifica que actualizar_sala() permite el mismo nombre."""
        servicio = SalaService(db_test)
        sala = servicio.crear_sala(SalaCreate(
            nombre="Aula",
            piso=1,
            capacidad=30,
            tipo_sala="Aula",
        ))

        # Actualizar solo la capacidad, manteniendo el nombre
        actualizada = servicio.actualizar_sala(sala.id, SalaUpdate(capacidad=50))

        assert actualizada.nombre == "Aula"
        assert actualizada.capacidad == 50

    def test_eliminar_sala_inexistente_lanza_404(self, db_test):
        """Verifica que eliminar_sala() lanza 404 si no existe."""
        servicio = SalaService(db_test)

        with pytest.raises(HTTPException) as exc_info:
            servicio.eliminar_sala(999)

        assert exc_info.value.status_code == 404

    def test_paginacion_invalida_rechazada(self, db_test):
        """Verifica que obtener_todas_salas() rechaza paginación inválida."""
        servicio = SalaService(db_test)

        with pytest.raises(HTTPException) as exc_info:
            servicio.obtener_todas_salas(skip=-1)

        assert exc_info.value.status_code == 400

    def test_limit_mayor_a_100_rechazado(self, db_test):
        """Verifica que obtener_todas_salas() rechaza limit > 100."""
        servicio = SalaService(db_test)

        with pytest.raises(HTTPException) as exc_info:
            servicio.obtener_todas_salas(limit=150)

        assert exc_info.value.status_code == 400


class TestSalaRoutes:
    """Tests de caracterización para rutas HTTP."""

    def test_obtener_salas_retorna_200(self):
        """Verifica que GET /api/v1/salas devuelve 200."""
        response = client.get("/api/v1/salas")

        assert response.status_code == 200
        data = response.json()
        assert "salas" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data

    def test_crear_sala_retorna_201(self):
        """Verifica que POST /api/v1/salas devuelve 201."""
        payload = {
            "nombre": "Aula Nueva",
            "piso": 1,
            "capacidad": 30,
            "tipo_sala": "Aula",
        }

        response = client.post("/api/v1/salas", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Aula Nueva"
        assert data["id"] is not None

    def test_crear_sala_duplicada_retorna_409(self):
        """Verifica que crear sala con nombre duplicado retorna 409."""
        payload = {
            "nombre": "Duplicada",
            "piso": 1,
            "capacidad": 30,
            "tipo_sala": "Aula",
        }

        client.post("/api/v1/salas", json=payload)
        response = client.post("/api/v1/salas", json=payload)

        assert response.status_code == 409

    def test_obtener_sala_inexistente_retorna_404(self):
        """Verifica que GET /api/v1/salas/999 retorna 404."""
        response = client.get("/api/v1/salas/999")

        assert response.status_code == 404

    def test_actualizar_sala_retorna_200(self):
        """Verifica que PUT /api/v1/salas/{id} retorna 200."""
        # Crear sala
        crear = client.post("/api/v1/salas", json={
            "nombre": "Original",
            "piso": 1,
            "capacidad": 30,
            "tipo_sala": "Aula",
        })
        sala_id = crear.json()["id"]

        # Actualizar
        response = client.put(f"/api/v1/salas/{sala_id}", json={
            "capacidad": 50,
        })

        assert response.status_code == 200
        assert response.json()["capacidad"] == 50

    def test_eliminar_sala_retorna_204(self):
        """Verifica que DELETE /api/v1/salas/{id} retorna 204."""
        # Crear sala
        crear = client.post("/api/v1/salas", json={
            "nombre": "Eliminar",
            "piso": 1,
            "capacidad": 30,
            "tipo_sala": "Aula",
        })
        sala_id = crear.json()["id"]

        # Eliminar
        response = client.delete(f"/api/v1/salas/{sala_id}")

        assert response.status_code == 204

    def test_obtener_salas_con_filtro_funciona(self):
        """Verifica que los filtros en GET /salas funcionan."""
        # Crear salas de diferentes tipos
        client.post("/api/v1/salas", json={
            "nombre": "Aula 1",
            "piso": 1,
            "capacidad": 30,
            "tipo_sala": "Aula",
        })
        client.post("/api/v1/salas", json={
            "nombre": "Lab 1",
            "piso": 2,
            "capacidad": 20,
            "tipo_sala": "Laboratorio",
        })

        response = client.get("/api/v1/salas?tipo_sala=Aula")

        assert response.status_code == 200
        assert len(response.json()["salas"]) == 1
        assert response.json()["salas"][0]["tipo_sala"] == "Aula"
