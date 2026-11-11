"""Controlador de informacion del modelo."""
from app.models.recomendador import Recomendador
from app.schemas.modelo import InfoModeloSalida


def obtener_info_modelo(recomendador: Recomendador) -> InfoModeloSalida:
    metadatos = recomendador.metadatos
    return InfoModeloSalida(
        nombre=metadatos["modelo"],
        datos_entrenamiento=metadatos["datos_entrenamiento"],
        emparejamiento=metadatos["emparejamiento"],
        sugerencias=metadatos["sugerencias"],
        perfiles=metadatos["perfiles"]["nombres"],
        version_sklearn=metadatos["version_sklearn"],
    )
