"""Vista del catalogo de habilidades (p. ej. para autocompletar en un formulario)."""
from fastapi import APIRouter, Depends, Query

from app.controllers import habilidad_controller
from app.core.dependencias import obtener_normalizador
from app.models.normalizador_habilidades import NormalizadorHabilidades
from app.schemas.habilidad import CatalogoSalida

router = APIRouter(prefix="/habilidades", tags=["Habilidades"])


@router.get("", response_model=CatalogoSalida, summary="Catálogo de habilidades reconocidas")
def listar_habilidades(
    categoria: str | None = Query(default=None, description="Filtrar por categoría, p. ej. 'Lenguajes'"),
    busqueda: str | None = Query(default=None, min_length=1, max_length=100, description="Texto contenido en el nombre"),
    normalizador: NormalizadorHabilidades = Depends(obtener_normalizador),
) -> CatalogoSalida:
    return habilidad_controller.listar_habilidades(normalizador, categoria, busqueda)
