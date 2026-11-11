"""Esquema de salida con la informacion del modelo entrenado."""
from typing import Any

from pydantic import BaseModel


class InfoModeloSalida(BaseModel):
    nombre: str
    datos_entrenamiento: dict[str, Any]
    emparejamiento: dict[str, Any]
    sugerencias: dict[str, Any]
    perfiles: list[str]
    version_sklearn: str
