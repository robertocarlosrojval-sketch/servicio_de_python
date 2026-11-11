"""Punto de entrada de la API.

Ejecutar desde la carpeta backend/:
    python -m app
(usa el host y el puerto de la configuracion; por defecto 127.0.0.1:8000)
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import obtener_configuracion
from app.core.errores import SinHabilidadesTecnicasError
from app.models.normalizador_habilidades import NormalizadorHabilidades
from app.models.recomendador import Recomendador
from app.views import router_api

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def ciclo_de_vida(app: FastAPI):
    """Carga el modelo una sola vez al iniciar el servidor."""
    configuracion = obtener_configuracion()
    try:
        app.state.recomendador = Recomendador.cargar(configuracion.ruta_modelo, configuracion.ruta_metadatos)
        app.state.normalizador = NormalizadorHabilidades.cargar(configuracion.ruta_normalizacion)
        logger.info("Modelo cargado desde %s", configuracion.ruta_modelo)
    except Exception:
        #El servidor arranca igualmente: /salud informa el problema y el resto responde 503
        app.state.recomendador = None
        app.state.normalizador = None
        logger.exception("No se pudo cargar el modelo")

    if configuracion.api_key is None:
        logger.warning("API_KEY no está definida: los endpoints no exigen el header X-API-Key")
    yield


async def manejar_sin_habilidades(request: Request, error: SinHabilidadesTecnicasError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": str(error), "habilidades_no_reconocidas": error.habilidades_no_reconocidas},
    )


def crear_app() -> FastAPI:
    configuracion = obtener_configuracion()
    app = FastAPI(
        title=configuracion.nombre_app,
        version=configuracion.version,
        description=(
            "Microservicio de machine learning de la plataforma de residencias profesionales: "
            "recomienda proyectos a los alumnos según sus habilidades, sugiere habilidades por aprender "
            "e identifica su perfil profesional."
        ),
        lifespan=ciclo_de_vida,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=configuracion.cors_origenes,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.add_exception_handler(SinHabilidadesTecnicasError, manejar_sin_habilidades)
    app.include_router(router_api, prefix=configuracion.prefijo_api)
    return app


app = crear_app()
