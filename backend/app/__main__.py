"""Arranca el servidor con el host y el puerto de la configuracion.

Ejecutar desde la carpeta backend/:
    python -m app
"""
import uvicorn

from app.core.config import obtener_configuracion

if __name__ == "__main__":
    configuracion = obtener_configuracion()
    uvicorn.run("app.main:app", host=configuracion.host, port=configuracion.puerto, reload=configuracion.recarga)
