from pathlib import Path

import pytest

from app.core.config import CARPETA_ARTEFACTOS, RAIZ_BACKEND

ARTEFACTOS = ["modelo_recomendador.pkl", "metadatos_recomendador.json", "normalizacion_habilidades.json"]
CARPETA_ENTRENAMIENTO = Path(RAIZ_BACKEND).parent / "analisis" / "modelo" / "artefactos"


@pytest.mark.parametrize("nombre", ARTEFACTOS)
def test_artefacto_esta_dentro_del_backend(nombre):
    assert (CARPETA_ARTEFACTOS / nombre).is_file()


@pytest.mark.parametrize("nombre", ARTEFACTOS)
def test_artefacto_coincide_con_el_ultimo_entrenamiento(nombre):
    #Avisa si se reentreno el modelo y no se copio a backend/artefactos
    original = CARPETA_ENTRENAMIENTO / nombre
    if not original.is_file():
        pytest.skip("La carpeta de entrenamiento no está disponible (backend aislado)")
    assert (CARPETA_ARTEFACTOS / nombre).read_bytes() == original.read_bytes()
