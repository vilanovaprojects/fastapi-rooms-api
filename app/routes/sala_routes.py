from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config import get_db
from app.schemas.sala_schema import SalaCreate, SalaResponse, SalaUpdate
from app.services.sala_service import SalaService

router = APIRouter(prefix="/api/v1/salas", tags=["salas"])


def get_sala_service(db: Session = Depends(get_db)) -> SalaService:
    return SalaService(db)


@router.get("", response_model=dict)
def obtener_salas(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    tipo_sala: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    service: SalaService = Depends(get_sala_service),
):
    return service.obtener_todas_salas(skip=skip, limit=limit, tipo_sala=tipo_sala, estado=estado)


@router.get("/{sala_id}", response_model=SalaResponse)
def obtener_sala(sala_id: int, service: SalaService = Depends(get_sala_service)):
    return service.obtener_sala_por_id(sala_id)


@router.post("", response_model=SalaResponse, status_code=status.HTTP_201_CREATED)
def crear_sala(sala: SalaCreate, service: SalaService = Depends(get_sala_service)):
    return service.crear_sala(sala)


@router.put("/{sala_id}", response_model=SalaResponse)
def actualizar_sala(
    sala_id: int,
    sala_data: SalaUpdate,
    service: SalaService = Depends(get_sala_service),
):
    return service.actualizar_sala(sala_id, sala_data)


@router.delete("/{sala_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_sala(sala_id: int, service: SalaService = Depends(get_sala_service)):
    service.eliminar_sala(sala_id)
    return None
