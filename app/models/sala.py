from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Sala(Base):
    """Representa una sala del entorno educativo.

    Esta entidad almacena la información básica de una sala, su estado,
    disponibilidad y metadatos de auditoría.
    """

    __tablename__ = "salas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    piso = Column(Integer, nullable=False)
    capacidad = Column(Integer, nullable=False)
    tipo_sala = Column(String(50), nullable=False)
    numero_ventanas = Column(Integer, nullable=True, default=0)
    tiene_proyector = Column(Boolean, default=False)
    tiene_aire_acondicionado = Column(Boolean, default=False)
    estado = Column(String(20), default="activa")
    descripcion = Column(String(500), nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
