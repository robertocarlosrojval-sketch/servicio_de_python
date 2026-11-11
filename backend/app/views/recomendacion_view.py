"""Vista de recomendaciones: endpoints que consume el backend de Spring Boot."""
from fastapi import APIRouter, Depends

from app.controllers import recomendacion_controller
from app.core.dependencias import obtener_normalizador, obtener_recomendador
from app.models.normalizador_habilidades import NormalizadorHabilidades
from app.models.recomendador import Recomendador
from app.schemas.recomendacion import (
    RespuestaHabilidades,
    RespuestaPerfil,
    RespuestaProyectos,
    SolicitudHabilidades,
    SolicitudPerfil,
    SolicitudProyectos,
)

router = APIRouter(prefix="/recomendaciones", tags=["Recomendaciones"])

RESPUESTA_SIN_HABILIDADES = {422: {"description": "Datos inválidos o ninguna habilidad técnica reconocida"}}


@router.post("/proyectos", response_model=RespuestaProyectos, responses=RESPUESTA_SIN_HABILIDADES,
             summary="Ordenar proyectos según su afinidad con el alumno")
def recomendar_proyectos(
    solicitud: SolicitudProyectos,
    recomendador: Recomendador = Depends(obtener_recomendador),
    normalizador: NormalizadorHabilidades = Depends(obtener_normalizador),
) -> RespuestaProyectos:
    return recomendacion_controller.recomendar_proyectos(solicitud, recomendador, normalizador)


@router.post("/habilidades", response_model=RespuestaHabilidades, responses=RESPUESTA_SIN_HABILIDADES,
             summary="Sugerir habilidades que le conviene aprender al alumno")
def sugerir_habilidades(
    solicitud: SolicitudHabilidades,
    recomendador: Recomendador = Depends(obtener_recomendador),
    normalizador: NormalizadorHabilidades = Depends(obtener_normalizador),
) -> RespuestaHabilidades:
    return recomendacion_controller.sugerir_habilidades(solicitud, recomendador, normalizador)


@router.post("/perfil", response_model=RespuestaPerfil, responses=RESPUESTA_SIN_HABILIDADES,
             summary="Identificar el perfil profesional del alumno")
def obtener_perfil(
    solicitud: SolicitudPerfil,
    recomendador: Recomendador = Depends(obtener_recomendador),
    normalizador: NormalizadorHabilidades = Depends(obtener_normalizador),
) -> RespuestaPerfil:
    return recomendacion_controller.obtener_perfil(solicitud, recomendador, normalizador)
