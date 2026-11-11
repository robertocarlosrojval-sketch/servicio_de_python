"""Esquema de salida del catalogo de habilidades."""
from pydantic import BaseModel


class HabilidadCatalogo(BaseModel):
    habilidad: str
    categoria: str


class CatalogoSalida(BaseModel):
    total: int
    habilidades: list[HabilidadCatalogo]
