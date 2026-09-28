from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_TIPOS_SALA = ["Aula", "Laboratorio", "Auditorio", "Oficina"]
VALID_ESTADOS = ["activa", "mantenimiento", "inhabitable"]


class SalaBase(BaseModel):
    """Modelo base para las validaciones comunes de una sala."""

    model_config = ConfigDict(from_attributes=True)

    nombre: str = Field(..., min_length=3, max_length=100)
    piso: int = Field(..., ge=1, le=10)
    capacidad: int = Field(..., ge=1, le=500)
    tipo_sala: str = Field(...)
    numero_ventanas: Optional[int] = Field(default=0, ge=0)
    tiene_proyector: bool = False
    tiene_aire_acondicionado: bool = False
    estado: str = Field(default="activa")
    descripcion: Optional[str] = Field(default=None, max_length=500)

    @field_validator("tipo_sala")
    @classmethod
    def validar_tipo_sala(cls, value: str) -> str:
        """Valida que el tipo de sala sea uno de los permitidos."""
        valor_normalizado = value.strip()
        if valor_normalizado not in VALID_TIPOS_SALA:
            raise ValueError(f"tipo_sala debe ser uno de: {', '.join(VALID_TIPOS_SALA)}")
        return valor_normalizado

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value: str) -> str:
        """Valida que el estado de la sala esté dentro de los permitidos."""
        valor_normalizado = value.strip().lower()
        if valor_normalizado not in VALID_ESTADOS:
            raise ValueError(f"estado debe ser uno de: {', '.join(VALID_ESTADOS)}")
        return valor_normalizado


class SalaCreate(SalaBase):
    """Schema para crear una nueva sala."""


class SalaUpdate(BaseModel):
    """Schema para actualización parcial de una sala."""

    model_config = ConfigDict(from_attributes=True)

    nombre: Optional[str] = Field(default=None, min_length=3, max_length=100)
    piso: Optional[int] = Field(default=None, ge=1, le=10)
    capacidad: Optional[int] = Field(default=None, ge=1, le=500)
    tipo_sala: Optional[str] = None
    numero_ventanas: Optional[int] = Field(default=None, ge=0)
    tiene_proyector: Optional[bool] = None
    tiene_aire_acondicionado: Optional[bool] = None
    estado: Optional[str] = None
    descripcion: Optional[str] = Field(default=None, max_length=500)

    @field_validator("tipo_sala")
    @classmethod
    def validar_tipo_sala(cls, value: Optional[str]) -> Optional[str]:
        """Valida el tipo de sala cuando se incluye en la actualización."""
        if value is None:
            return value

        valor_normalizado = value.strip()
        if valor_normalizado not in VALID_TIPOS_SALA:
            raise ValueError(f"tipo_sala debe ser uno de: {', '.join(VALID_TIPOS_SALA)}")
        return valor_normalizado

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, value: Optional[str]) -> Optional[str]:
        """Valida el estado cuando se incluye en la actualización."""
        if value is None:
            return value

        valor_normalizado = value.strip().lower()
        if valor_normalizado not in VALID_ESTADOS:
            raise ValueError(f"estado debe ser uno de: {', '.join(VALID_ESTADOS)}")
        return valor_normalizado


class SalaResponse(SalaBase):
    """Schema de respuesta estándar para una sala."""

    id: int
    fecha_creacion: datetime
    fecha_actualizacion: datetime
