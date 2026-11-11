from tests.conftest import PREFIJO


def test_salud_con_modelo_cargado(cliente):
    respuesta = cliente.get(f"{PREFIJO}/salud")
    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "ok"
    assert respuesta.json()["modelo_cargado"] is True


def test_info_modelo(cliente):
    respuesta = cliente.get(f"{PREFIJO}/modelo")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["nombre"] == "Recomendador de proyectos y habilidades"
    assert "Backend Java" in datos["perfiles"]
    assert datos["emparejamiento"]["precision_familia@10"] > datos["emparejamiento"]["precision_azar"]


def test_catalogo_filtra_por_categoria_y_busqueda(cliente):
    respuesta = cliente.get(f"{PREFIJO}/habilidades", params={"categoria": "Cloud", "busqueda": "aw"})
    assert respuesta.status_code == 200
    nombres = [h["habilidad"] for h in respuesta.json()["habilidades"]]
    assert "AWS" in nombres
    assert all(h["categoria"] == "Cloud" for h in respuesta.json()["habilidades"])


def test_catalogo_completo(cliente):
    datos = cliente.get(f"{PREFIJO}/habilidades").json()
    assert datos["total"] == len(datos["habilidades"]) > 1000
