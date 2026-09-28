from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.sala_repository import SalaRepository
from app.schemas.sala_schema import SalaCreate, SalaUpdate


class SalaService:
    def __init__(self, db: Session):
        self.repository = SalaRepository(db)

    def obtener_todas_salas(
        self,
        skip: int = 0,
        limit: int = 10,
        tipo_sala: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> dict:
        if skip < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="skip no puede ser negativo")
        if limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="limit debe estar entre 1 y 100",
            )

        salas = self.repository.filtrar(skip=skip, limit=limit, tipo_sala=tipo_sala, estado=estado)
        total = self.repository.contar_total()

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "salas": salas,
        }

    def obtener_sala_por_id(self, sala_id: int):
        sala = self.repository.obtener_por_id(sala_id)
        if not sala:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sala con ID {sala_id} no encontrada",
            )
        return sala

    def crear_sala(self, sala_data: SalaCreate):
        if self.repository.obtener_por_nombre(sala_data.nombre):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Una sala con el nombre '{sala_data.nombre}' ya existe",
            )

        try:
            return self.repository.crear(sala_data)
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    def actualizar_sala(self, sala_id: int, sala_data: SalaUpdate):
        sala_existente = self.repository.obtener_por_id(sala_id)
        if not sala_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sala con ID {sala_id} no encontrada",
            )

        if sala_data.nombre and sala_data.nombre != sala_existente.nombre:
            nombre_existente = self.repository.obtener_por_nombre(sala_data.nombre)
            if nombre_existente:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Una sala con el nombre '{sala_data.nombre}' ya existe",
                )

        try:
            return self.repository.actualizar(sala_id, sala_data)
        except Exception as exc:  # pragma: no cover
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    def eliminar_sala(self, sala_id: int) -> bool:
        eliminada = self.repository.eliminar(sala_id)
        if not eliminada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sala con ID {sala_id} no encontrada",
            )
        return True
