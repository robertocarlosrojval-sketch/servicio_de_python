"""Configuracion de la aplicacion.

Todos los valores se pueden sobrescribir con variables de entorno, asi el mismo
codigo sirve para desarrollo, pruebas y produccion sin modificarlo.
"""
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

#Carpeta backend/: backend/app/core/config.py -> subir 2 niveles
#Los artefactos viven dentro de backend/ para que el servicio se pueda desplegar por si solo
RAIZ_BACKEND = Path(__file__).resolve().parents[2]
CARPETA_ARTEFACTOS = RAIZ_BACKEND / "artefactos"


def _leer_lista(valor: str) -> list[str]:
    return [elemento.strip() for elemento in valor.split(",") if elemento.strip()]


@dataclass(frozen=True)
class Configuracion:
    nombre_app: str
    version: str
    host: str
    puerto: int
    recarga: bool
    prefijo_api: str
    ruta_modelo: Path
    ruta_metadatos: Path
    ruta_normalizacion: Path
    api_key: str | None
    cors_origenes: list[str]

    @classmethod
    def desde_entorno(cls) -> "Configuracion":
        return cls(
            nombre_app=os.getenv("APP_NOMBRE", "Microservicio de Recomendación de Residencias"),
            version=os.getenv("APP_VERSION", "2.0.0"),
            #8080 lo usa el backend de Spring Boot
            host=os.getenv("HOST", "127.0.0.1"),
            puerto=int(os.getenv("PUERTO", "8000")),
            recarga=os.getenv("RECARGA", "true").lower() in ("1", "true", "si", "sí"),
            prefijo_api=os.getenv("API_PREFIJO", "/api/v1"),
            ruta_modelo=Path(os.getenv("MODELO_RUTA", CARPETA_ARTEFACTOS / "modelo_recomendador.pkl")),
            ruta_metadatos=Path(os.getenv("METADATOS_RUTA", CARPETA_ARTEFACTOS / "metadatos_recomendador.json")),
            ruta_normalizacion=Path(os.getenv("NORMALIZACION_RUTA", CARPETA_ARTEFACTOS / "normalizacion_habilidades.json")),
            api_key=os.getenv("API_KEY") or None,
            cors_origenes=_leer_lista(os.getenv("CORS_ORIGENES", "http://localhost:3000,http://localhost:5173")),
        )


@lru_cache
def obtener_configuracion() -> Configuracion:
    """Devuelve la configuracion (se lee una sola vez y se reutiliza)."""
    return Configuracion.desde_entorno()
