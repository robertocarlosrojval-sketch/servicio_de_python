"""Vista de informacion del modelo."""
from fastapi import APIRouter, Depends

from app.controllers import modelo_controller
from app.core.dependencias import obtener_recomendador
from app.models.recomendador import Recomendador
from app.schemas.modelo import InfoModeloSalida

router = APIRouter(prefix="/modelo", tags=["Modelo"])


@router.get("", response_model=InfoModeloSalida, summary="Información y métricas del modelo")
def obtener_info(recomendador: Recomendador = Depends(obtener_recomendador)) -> InfoModeloSalida:
    return modelo_controller.obtener_info_modelo(recomendador)
