"""Controlador del estado del servicio."""
from app.schemas.salud import SaludSalida


def obtener_estado(modelo_cargado: bool, version: str) -> SaludSalida:
    return SaludSalida(
        estado="ok" if modelo_cargado else "degradado",
        modelo_cargado=modelo_cargado,
        version=version,
    )
