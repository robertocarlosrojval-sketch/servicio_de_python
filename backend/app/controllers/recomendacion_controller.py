"""Controlador de recomendaciones: normaliza las habilidades y consulta el modelo."""
from app.core.errores import SinHabilidadesTecnicasError
from app.models.normalizador_habilidades import NormalizadorHabilidades
from app.models.recomendador import Recomendador
from app.schemas.recomendacion import (
    HabilidadSugerida,
    ProyectoRecomendado,
    RespuestaHabilidades,
    RespuestaPerfil,
    RespuestaProyectos,
    SolicitudHabilidades,
    SolicitudPerfil,
    SolicitudProyectos,
)


def _normalizar_alumno(
    habilidades: list[str], normalizador: NormalizadorHabilidades, recomendador: Recomendador
) -> tuple[list[str], list[str]]:
    reconocidas, no_reconocidas = normalizador.normalizar(habilidades)
    if not any(recomendador.conoce(h) for h in reconocidas):
        raise SinHabilidadesTecnicasError(no_reconocidas)
    return reconocidas, no_reconocidas


def recomendar_proyectos(
    solicitud: SolicitudProyectos, recomendador: Recomendador, normalizador: NormalizadorHabilidades
) -> RespuestaProyectos:
    reconocidas, no_reconocidas = _normalizar_alumno(solicitud.habilidades, normalizador, recomendador)
    proyectos = [(proyecto, *normalizador.normalizar(proyecto.habilidades)) for proyecto in solicitud.proyectos]
    afinidades = recomendador.afinidades(reconocidas, [habilidades for _, habilidades, _ in proyectos])

    alumno = set(reconocidas)
    resultados = [
        ProyectoRecomendado(
            id=proyecto.id,
            titulo=proyecto.titulo,
            afinidad=round(afinidad, 4),
            habilidades_coincidentes=[h for h in habilidades if h in alumno],
            habilidades_faltantes=[h for h in habilidades if h not in alumno],
            habilidades_no_reconocidas=no_reconocidas_proyecto,
        )
        for (proyecto, habilidades, no_reconocidas_proyecto), afinidad in zip(proyectos, afinidades)
    ]
    resultados.sort(key=lambda resultado: resultado.afinidad, reverse=True)

    return RespuestaProyectos(
        habilidades_reconocidas=reconocidas,
        habilidades_no_reconocidas=no_reconocidas,
        total_proyectos=len(resultados),
        resultados=resultados[: solicitud.limite],
    )


def sugerir_habilidades(
    solicitud: SolicitudHabilidades, recomendador: Recomendador, normalizador: NormalizadorHabilidades
) -> RespuestaHabilidades:
    reconocidas, no_reconocidas = _normalizar_alumno(solicitud.habilidades, normalizador, recomendador)
    sugerencias = recomendador.sugerir_habilidades(reconocidas, solicitud.limite)
    return RespuestaHabilidades(
        habilidades_reconocidas=reconocidas,
        habilidades_no_reconocidas=no_reconocidas,
        sugerencias=[
            HabilidadSugerida(habilidad=habilidad, categoria=categoria, relevancia=relevancia)
            for habilidad, categoria, relevancia in sugerencias
        ],
    )


def obtener_perfil(
    solicitud: SolicitudPerfil, recomendador: Recomendador, normalizador: NormalizadorHabilidades
) -> RespuestaPerfil:
    reconocidas, no_reconocidas = _normalizar_alumno(solicitud.habilidades, normalizador, recomendador)
    perfil, habilidades_clave = recomendador.perfil(reconocidas)
    return RespuestaPerfil(
        habilidades_reconocidas=reconocidas,
        habilidades_no_reconocidas=no_reconocidas,
        perfil=perfil,
        habilidades_clave=habilidades_clave,
        habilidades_clave_faltantes=[h for h in habilidades_clave if h not in reconocidas],
    )
