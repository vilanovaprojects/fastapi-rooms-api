from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.sala import Sala
from app.schemas.sala_schema import SalaCreate, SalaUpdate


class BaseRepository:
    """Define la dependencia compartida hacia la sesión de base de datos."""

    def __init__(self, db: Session):
        self.db = db


class SalaRepository(BaseRepository):
    """Encapsula las operaciones de persistencia para entidades Sala."""

    def __init__(self, db: Session):
        super().__init__(db)

    def obtener_todos(self, skip: int = 0, limit: int = 10) -> list[Sala]:
        """Obtiene una página de salas ordenadas por id.

        Args:
            skip: Número de registros a omitir.
            limit: Número máximo de registros a devolver.

        Returns:
            Lista de salas paginadas.
        """
        return self.db.query(Sala).offset(skip).limit(limit).all()

    def obtener_por_id(self, sala_id: int) -> Optional[Sala]:
        """Busca una sala por su identificador.

        Args:
            sala_id: Identificador único de la sala.

        Returns:
            La sala encontrada o None si no existe.
        """
        return self.db.query(Sala).filter(Sala.id == sala_id).first()

    def obtener_por_nombre(self, nombre: str) -> Optional[Sala]:
        """Busca una sala por su nombre exacto.

        Args:
            nombre: Nombre completo de la sala.

        Returns:
            La sala encontrada o None si no existe.
        """
        return self.db.query(Sala).filter(Sala.nombre == nombre).first()

    def filtrar(
        self,
        skip: int = 0,
        limit: int = 10,
        tipo_sala: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> list[Sala]:
        """Aplica filtros de búsqueda y paginación sobre salas.

        Args:
            skip: Número de registros a omitir.
            limit: Número máximo de registros a devolver.
            tipo_sala: Filtro por tipo de sala, si aplica.
            estado: Filtro por estado de sala, si aplica.

        Returns:
            Lista de salas que cumplen los filtros.
        """
        query = self._crear_consulta_filtrada(tipo_sala=tipo_sala, estado=estado)
        return query.offset(skip).limit(limit).all()

    def _crear_consulta_filtrada(
        self,
        tipo_sala: Optional[str] = None,
        estado: Optional[str] = None,
    ):
        """Construye la query base aplicando los filtros opcionales.

        Args:
            tipo_sala: Filtro por tipo de sala.
            estado: Filtro por estado.

        Returns:
            Query de SQLAlchemy con filtros aplicados.
        """
        query = self.db.query(Sala)

        if tipo_sala:
            query = query.filter(Sala.tipo_sala == tipo_sala)
        if estado:
            query = query.filter(Sala.estado == estado)

        return query

    def contar_total(self) -> int:
        """Devuelve la cantidad total de salas registradas."""
        return self.db.query(Sala).count()

    def crear(self, sala_data: SalaCreate) -> Sala:
        """Crea una nueva sala a partir de datos validados.

        Args:
            sala_data: Datos de creación de la sala.

        Returns:
            La sala persistida con su ID generado.
        """
        nueva_sala = Sala(**sala_data.model_dump())
        self.db.add(nueva_sala)
        self.db.commit()
        self.db.refresh(nueva_sala)
        return nueva_sala

    def actualizar(self, sala_id: int, sala_data: SalaUpdate) -> Optional[Sala]:
        """Actualiza una sala existente con los datos recibidos.

        Args:
            sala_id: Identificador de la sala a actualizar.
            sala_data: Datos parciales o completos a aplicar.

        Returns:
            La sala actualizada o None si no existe.
        """
        sala_existente = self.obtener_por_id(sala_id)
        if not sala_existente:
            return None

        datos_actualizacion = sala_data.model_dump(exclude_unset=True)
        for nombre_campo, valor in datos_actualizacion.items():
            setattr(sala_existente, nombre_campo, valor)

        self.db.commit()
        self.db.refresh(sala_existente)
        return sala_existente

    def eliminar(self, sala_id: int) -> bool:
        """Elimina una sala si existe.

        Args:
            sala_id: Identificador de la sala a eliminar.

        Returns:
            True si la eliminación tuvo éxito; False si la sala no existe.
        """
        sala_existente = self.obtener_por_id(sala_id)
        if not sala_existente:
            return False

        self.db.delete(sala_existente)
        self.db.commit()
        return True
