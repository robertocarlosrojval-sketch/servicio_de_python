"""Esquema de salida del estado del servicio."""
from typing import Literal

from pydantic import BaseModel


class SaludSalida(BaseModel):
    estado: Literal["ok", "degradado"]
    modelo_cargado: bool
    version: str
