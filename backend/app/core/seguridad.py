"""Autenticacion entre servicios con una clave compartida (header X-API-Key).

Si la variable de entorno API_KEY no esta definida, la verificacion se desactiva
(util en desarrollo). En produccion debe definirse con el mismo valor que use el
backend de Spring Boot.
"""
import secrets

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import Configuracion, obtener_configuracion

esquema_api_key = APIKeyHeader(name="X-API-Key", auto_error=False)


def verificar_api_key(
    api_key: str | None = Security(esquema_api_key),
    configuracion: Configuracion = Depends(obtener_configuracion),
) -> None:
    if configuracion.api_key is None:
        return
    if api_key is None or not secrets.compare_digest(api_key, configuracion.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave de API inválida o ausente (header X-API-Key).",
        )
