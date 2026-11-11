"""Vista del estado del servicio."""
from fastapi import APIRouter, Depends, Response, status

from app.controllers import salud_controller
from app.core.config import Configuracion, obtener_configuracion
from app.core.dependencias import modelo_disponible
from app.schemas.salud import SaludSalida

router = APIRouter(prefix="/salud", tags=["Salud"])


@router.get("", response_model=SaludSalida, summary="Estado del servicio")
def obtener_estado(
    response: Response,
    modelo_cargado: bool = Depends(modelo_disponible),
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> SaludSalida:
    #Render usa esta ruta como health check: sin modelo el despliegue no debe darse por bueno
    if not modelo_cargado:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return salud_controller.obtener_estado(modelo_cargado, configuracion.version)
