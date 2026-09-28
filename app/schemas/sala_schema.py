from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config import get_db
from app.schemas.sala_schema import SalaCreate, SalaResponse, SalaUpdate
from app.services.sala_service import SalaService

router = APIRouter(prefix="/api/v1/salas", tags=["salas"])


def get_sala_service(db: Session = Depends(get_db)) -> SalaService:
    """Crea la instancia del servicio de salas para una petición."""
    return SalaService(db)


@router.get("", response_model=dict)
def obtener_salas(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    tipo_sala: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    service: SalaService = Depends(get_sala_service),
) -> dict:
    """Obtiene todas las salas con paginación y filtros opcionales.

    Args:
        skip: Número de registros a omitir.
        limit: Cantidad máxima de registros a devolver.
        tipo_sala: Filtro opcional por tipo de sala.
        estado: Filtro opcional por estado.
        service: Servicio de negocio inyectado.

    Returns:
        Dicionario con total, paginación y lista de salas.
    """
    return service.obtener_todas_salas(
        skip=skip,
        limit=limit,
        tipo_sala=tipo_sala,
        estado=estado,
    )


@router.get("/{sala_id}", response_model=SalaResponse)
def obtener_sala(
    sala_id: int,
    service: SalaService = Depends(get_sala_service),
) -> SalaResponse:
    """Obtiene una sala por su identificador.

    Args:
        sala_id: ID de la sala a consultar.
        service: Servicio de negocio inyectado.

    Returns:
        Datos completos de la sala.
    """
    return service.obtener_sala_por_id(sala_id)


@router.post("", response_model=SalaResponse, status_code=status.HTTP_201_CREATED)
def crear_sala(
    sala: SalaCreate,
    service: SalaService = Depends(get_sala_service),
) -> SalaResponse:
    """Crea una nueva sala en el sistema.

    Args:
        sala: Datos de la nueva sala.
        service: Servicio de negocio inyectado.

    Returns:
        La sala creada.
    """
    return service.crear_sala(sala)


@router.put("/{sala_id}", response_model=SalaResponse)
def actualizar_sala(
    sala_id: int,
    sala_data: SalaUpdate,
    service: SalaService = Depends(get_sala_service),
) -> SalaResponse:
    """Actualiza una sala existente.

    Args:
        sala_id: ID de la sala a actualizar.
        sala_data: Datos nuevos para la sala.
        service: Servicio de negocio inyectado.

    Returns:
        La sala actualizada.
    """
    return service.actualizar_sala(sala_id, sala_data)


@router.delete("/{sala_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_sala(
    sala_id: int,
    service: SalaService = Depends(get_sala_service),
) -> None:
    """Elimina una sala por su identificador.

    Args:
        sala_id: ID de la sala a eliminar.
        service: Servicio de negocio inyectado.
    """
    service.eliminar_sala(sala_id)
    return None
