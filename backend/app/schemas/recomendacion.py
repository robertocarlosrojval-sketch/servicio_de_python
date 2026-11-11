"""Esquemas de entrada y salida de las recomendaciones.

Definen el contrato con el backend de Spring Boot: que datos se reciben, como se
validan y que forma tiene la respuesta.
"""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

MAX_HABILIDADES = 100
MAX_PROYECTOS = 500

Habilidad = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
ListaHabilidades = Annotated[list[Habilidad], Field(min_length=1, max_length=MAX_HABILIDADES)]

EJEMPLO_HABILIDADES = ["Java", "Spring Boot", "SQL", "Git", "HTML"]


class HabilidadesNormalizadas(BaseModel):
    habilidades_reconocidas: list[str] = Field(description="Habilidades del alumno con su nombre normalizado")
    habilidades_no_reconocidas: list[str] = Field(description="Habilidades que el modelo no conoce (se ignoran)")


#--- Recomendacion de proyectos ---

class ProyectoEntrada(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int | str = Field(description="Identificador del proyecto en la plataforma")
    titulo: str | None = Field(default=None, max_length=300)
    habilidades: Annotated[list[Habilidad], Field(max_length=MAX_HABILIDADES)]


class SolicitudProyectos(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={"examples": [{
        "habilidades": EJEMPLO_HABILIDADES,
        "proyectos": [
            {"id": 1, "titulo": "Sistema de inventarios web",
             "habilidades": ["Java", "Spring Boot", "PostgreSQL", "REST API", "Docker"]},
            {"id": 2, "titulo": "Firmware para sensor IoT",
             "habilidades": ["C", "Embedded Systems", "RTOS", "I2C"]},
        ],
        "limite": 10,
    }]})

    habilidades: ListaHabilidades = Field(description="Habilidades del alumno")
    proyectos: list[ProyectoEntrada] = Field(min_length=1, max_length=MAX_PROYECTOS)
    limite: int = Field(default=10, ge=1, le=MAX_PROYECTOS, description="Número máximo de proyectos a devolver")


class ProyectoRecomendado(BaseModel):
    id: int | str
    titulo: str | None
    afinidad: float = Field(ge=0, le=1, description="Similitud entre el alumno y el proyecto (0 a 1)")
    habilidades_coincidentes: list[str]
    habilidades_faltantes: list[str]
    habilidades_no_reconocidas: list[str]


class RespuestaProyectos(HabilidadesNormalizadas):
    total_proyectos: int
    resultados: list[ProyectoRecomendado]


#--- Habilidades sugeridas ---

class SolicitudHabilidades(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={"examples": [
        {"habilidades": EJEMPLO_HABILIDADES, "limite": 8}
    ]})

    habilidades: ListaHabilidades
    limite: int = Field(default=10, ge=1, le=50)


class HabilidadSugerida(BaseModel):
    habilidad: str
    categoria: str
    relevancia: float = Field(ge=0, le=1, description="Relevancia relativa a la primera sugerencia (1.0)")


class RespuestaHabilidades(HabilidadesNormalizadas):
    sugerencias: list[HabilidadSugerida]


#--- Perfil profesional ---

class SolicitudPerfil(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={"examples": [{"habilidades": EJEMPLO_HABILIDADES}]})

    habilidades: ListaHabilidades


class RespuestaPerfil(HabilidadesNormalizadas):
    perfil: str
    habilidades_clave: list[str] = Field(description="Habilidades más representativas del perfil")
    habilidades_clave_faltantes: list[str] = Field(description="Habilidades clave del perfil que el alumno no tiene")
