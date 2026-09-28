from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.sala import Sala
from app.repositories.sala_repository import SalaRepository
from app.schemas.sala_schema import SalaCreate, SalaUpdate


class SalaService:
    """Gestiona la lógica de negocio de las salas.

    Esta clase centraliza validaciones, reglas de negocio y coordinación con
    el repositorio de persistencia.
    """

    def __init__(self, db: Session):
        self.repository = SalaRepository(db)

    def obtener_todas_salas(
        self,
        skip: int = 0,
        limit: int = 10,
        tipo_sala: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> dict:
        """Obtiene las salas con paginación y filtros opcionales.

        Args:
            skip: Número de registros a omitir.
            limit: Cantidad máxima de registros a devolver.
            tipo_sala: Filtro por tipo de sala.
            estado: Filtro por estado de la sala.

        Returns:
            Diccionario con total, paginación y lista de salas.

        Raises:
            HTTPException: Si los parámetros de paginación son inválidos.
        """
        self._validar_parametros_paginacion(skip=skip, limit=limit)

        salas = self.repository.filtrar(
            skip=skip,
            limit=limit,
            tipo_sala=tipo_sala,
            estado=estado,
        )
        total_salas = self.repository.contar_total()

        return {
            "total": total_salas,
            "skip": skip,
            "limit": limit,
            "salas": salas,
        }

    def obtener_sala_por_id(self, sala_id: int) -> Sala:
        """Obtiene una sala por su identificador.

        Args:
            sala_id: Identificador único de la sala.

        Returns:
            La sala consultada.

        Raises:
            HTTPException: Si la sala no existe.
        """
        sala = self.repository.obtener_por_id(sala_id)
        if not sala:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sala con ID {sala_id} no encontrada",
            )
        return sala

    def crear_sala(self, sala_data: SalaCreate) -> Sala:
        """Crea una nueva sala con validaciones de negocio.

        Args:
            sala_data: Datos de la sala a persistir.

        Returns:
            La sala creada.

        Raises:
            HTTPException: Si el nombre ya existe o si hay error persistente.
        """
        self._validar_nombre_unico_para_creacion(sala_data.nombre)

        try:
            return self.repository.crear(sala_data)
        except Exception as exc:  # pragma: no cover - se maneja en capa de infra
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    def actualizar_sala(self, sala_id: int, sala_data: SalaUpdate) -> Sala:
        """Actualiza una sala existente.

        Args:
            sala_id: Identificador de la sala.
            sala_data: Datos a actualizar.

        Returns:
            La sala actualizada.

        Raises:
            HTTPException: Si la sala no existe o si el nombre ya existe.
        """
        sala_existente = self._obtener_sala_o_error(sala_id)
        self._validar_nombre_unico_para_actualizacion(
            sala_id=sala_id,
            nombre=sala_data.nombre,
            nombre_actual=sala_existente.nombre,
        )

        try:
            sala_actualizada = self.repository.actualizar(sala_id, sala_data)
            if not sala_actualizada:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Sala con ID {sala_id} no encontrada",
                )
            return sala_actualizada
        except HTTPException:
            raise
        except Exception as exc:  # pragma: no cover - error de persistencia
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

    def eliminar_sala(self, sala_id: int) -> bool:
        """Elimina la sala indicada por ID.

        Args:
            sala_id: Identificador de la sala.

        Returns:
            True si se eliminó correctamente.

        Raises:
            HTTPException: Si la sala no existe.
        """
        fue_eliminada = self.repository.eliminar(sala_id)
        if not fue_eliminada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sala con ID {sala_id} no encontrada",
            )
        return True

    def _validar_parametros_paginacion(self, skip: int, limit: int) -> None:
        """Valida reglas de paginación.

        Args:
            skip: Número de registros a omitir.
            limit: Número de registros solicitados.

        Raises:
            HTTPException: Si la paginación es inválida.
        """
        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="skip no puede ser negativo",
            )
        if limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="limit debe estar entre 1 y 100",
            )

    def _validar_nombre_unico_para_creacion(self, nombre: str) -> None:
        """Valida que una sala con el mismo nombre no exista.

        Args:
            nombre: Nombre de la sala a crear.

        Raises:
            HTTPException: Si ya existe una sala con ese nombre.
        """
        sala_existente = self.repository.obtener_por_nombre(nombre)
        if sala_existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Una sala con el nombre '{nombre}' ya existe",
            )

    def _validar_nombre_unico_para_actualizacion(
        self,
        sala_id: int,
        nombre: Optional[str],
        nombre_actual: str,
    ) -> None:
        """Valida unicidad del nombre al actualizar, evitando duplicados.

        Args:
            sala_id: Identificador actual de la sala.
            nombre: Nuevo nombre proporcionado.
            nombre_actual: Nombre actual antes del cambio.

        Raises:
            HTTPException: Si el nombre ya existe en otra sala.
        """
        if nombre and nombre != nombre_actual:
            sala_con_nombre = self.repository.obtener_por_nombre(nombre)
            if sala_con_nombre and sala_con_nombre.id != sala_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Una sala con el nombre '{nombre}' ya existe",
                )

    def _obtener_sala_o_error(self, sala_id: int) -> Sala:
        """Obtiene una sala o lanza un error 404.

        Args:
            sala_id: Identificador de la sala a buscar.

        Returns:
            La sala encontrada.

        Raises:
            HTTPException: Si la sala no existe.
        """
        sala = self.repository.obtener_por_id(sala_id)
        if not sala:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Sala con ID {sala_id} no encontrada",
            )
        return sala
