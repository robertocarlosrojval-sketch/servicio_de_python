"""Dependencias compartidas que FastAPI inyecta en las vistas."""
from fastapi import HTTPException, Request, status

from app.models.normalizador_habilidades import NormalizadorHabilidades
from app.models.recomendador import Recomendador


def modelo_disponible(request: Request) -> bool:
    estado = request.app.state
    return getattr(estado, "recomendador", None) is not None and getattr(estado, "normalizador", None) is not None


def _servicio_no_disponible() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="El modelo no está disponible. Revisa los registros del servidor.",
    )


def obtener_recomendador(request: Request) -> Recomendador:
    """Devuelve el recomendador cargado o responde 503 si no esta disponible."""
    if not modelo_disponible(request):
        raise _servicio_no_disponible()
    return request.app.state.recomendador


def obtener_normalizador(request: Request) -> NormalizadorHabilidades:
    if not modelo_disponible(request):
        raise _servicio_no_disponible()
    return request.app.state.normalizador
