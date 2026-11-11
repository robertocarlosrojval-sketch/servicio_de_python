"""Vistas: agrupa los routers de la API en uno solo.

Para agregar un recurso nuevo, crea su archivo *_view.py y registralo aqui.
"""
from fastapi import APIRouter, Depends

from app.core.seguridad import verificar_api_key
from app.views import habilidad_view, modelo_view, recomendacion_view, salud_view

router_api = APIRouter()

#La salud queda abierta para los monitores; el resto exige la clave entre servicios
router_api.include_router(salud_view.router)

router_protegido = APIRouter(dependencies=[Depends(verificar_api_key)])
router_protegido.include_router(modelo_view.router)
router_protegido.include_router(habilidad_view.router)
router_protegido.include_router(recomendacion_view.router)
router_api.include_router(router_protegido)
