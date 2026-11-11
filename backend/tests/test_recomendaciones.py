from dataclasses import replace

import pytest

from app.core.config import obtener_configuracion
from app.schemas.recomendacion import MAX_HABILIDADES, MAX_PROYECTOS
from tests.conftest import ALUMNO_JAVA, PREFIJO, PROYECTOS

URL = f"{PREFIJO}/recomendaciones"


#--- Proyectos ---

def test_proyecto_mas_afin_primero(cliente):
    respuesta = cliente.post(f"{URL}/proyectos", json={"habilidades": ALUMNO_JAVA, "proyectos": PROYECTOS})
    assert respuesta.status_code == 200
    resultados = respuesta.json()["resultados"]
    assert resultados[0]["id"] == 1
    assert resultados[-1]["id"] == 4
    afinidades = [r["afinidad"] for r in resultados]
    assert afinidades == sorted(afinidades, reverse=True)
    assert all(0 <= a <= 1 for a in afinidades)


def test_coincidencias_y_faltantes(cliente):
    datos = cliente.post(f"{URL}/proyectos", json={"habilidades": ALUMNO_JAVA, "proyectos": PROYECTOS[:1]}).json()
    proyecto = datos["resultados"][0]
    assert proyecto["habilidades_coincidentes"] == ["Java", "Spring Boot"]
    assert proyecto["habilidades_faltantes"] == ["PostgreSQL", "REST API", "Docker"]


def test_habilidades_escritas_de_otra_forma_se_normalizan(cliente):
    alumno = ["java", "springboot", "Tecnologia Inventada"]
    proyectos = [{"id": "A-1", "habilidades": ["JAVA", "Spring Boot", "Otra Inventada"]}]
    datos = cliente.post(f"{URL}/proyectos", json={"habilidades": alumno, "proyectos": proyectos}).json()
    assert datos["habilidades_reconocidas"] == ["Java", "Spring Boot"]
    assert datos["habilidades_no_reconocidas"] == ["Tecnologia Inventada"]
    assert datos["resultados"][0]["id"] == "A-1"
    assert datos["resultados"][0]["habilidades_no_reconocidas"] == ["Otra Inventada"]
    assert datos["resultados"][0]["afinidad"] > 0.9


def test_limite_de_resultados(cliente):
    datos = cliente.post(f"{URL}/proyectos", json={"habilidades": ALUMNO_JAVA, "proyectos": PROYECTOS, "limite": 2}).json()
    assert datos["total_proyectos"] == 4
    assert len(datos["resultados"]) == 2


def test_proyecto_sin_habilidades_reconocidas_tiene_afinidad_cero(cliente):
    proyectos = [{"id": 9, "habilidades": []}]
    datos = cliente.post(f"{URL}/proyectos", json={"habilidades": ALUMNO_JAVA, "proyectos": proyectos}).json()
    assert datos["resultados"][0]["afinidad"] == 0


#--- Habilidades sugeridas ---

def test_sugerencias_no_incluyen_lo_que_ya_sabe(cliente):
    respuesta = cliente.post(f"{URL}/habilidades", json={"habilidades": ALUMNO_JAVA, "limite": 8})
    assert respuesta.status_code == 200
    sugerencias = respuesta.json()["sugerencias"]
    assert len(sugerencias) == 8
    assert not {s["habilidad"] for s in sugerencias} & set(ALUMNO_JAVA)
    assert sugerencias[0]["relevancia"] == 1.0


def test_sugerencias_coherentes_con_el_perfil(cliente):
    sugerencias = cliente.post(f"{URL}/habilidades", json={"habilidades": ["HTML", "CSS", "JavaScript"]}).json()["sugerencias"]
    nombres = {s["habilidad"] for s in sugerencias}
    assert nombres & {"React", "Angular", "TypeScript", "jQuery"}


#--- Perfil ---

@pytest.mark.parametrize("habilidades, perfil", [
    (ALUMNO_JAVA, "Backend Java"),
    (["C", "Embedded Systems", "RTOS", "I2C", "SPI"], "Desarrollo embebido"),
    (["C#", ".NET", "SQL Server", "ASP.NET"], "Desarrollo .NET"),
])
def test_perfil(cliente, habilidades, perfil):
    datos = cliente.post(f"{URL}/perfil", json={"habilidades": habilidades}).json()
    assert datos["perfil"] == perfil
    assert not set(datos["habilidades_clave_faltantes"]) & set(datos["habilidades_reconocidas"])


#--- Validacion y errores ---

@pytest.mark.parametrize("endpoint", ["proyectos", "habilidades", "perfil"])
def test_sin_habilidades_tecnicas_devuelve_422(cliente, endpoint):
    cuerpo = {"habilidades": ["Communication", "Inventada"]}
    if endpoint == "proyectos":
        cuerpo["proyectos"] = PROYECTOS
    respuesta = cliente.post(f"{URL}/{endpoint}", json=cuerpo)
    assert respuesta.status_code == 422
    assert respuesta.json()["habilidades_no_reconocidas"] == ["Inventada"]


@pytest.mark.parametrize("cuerpo", [
    {"habilidades": [], "proyectos": PROYECTOS},
    {"habilidades": ALUMNO_JAVA, "proyectos": []},
    {"habilidades": ["   "], "proyectos": PROYECTOS},
    {"habilidades": ["Java"] * (MAX_HABILIDADES + 1), "proyectos": PROYECTOS},
    {"habilidades": ALUMNO_JAVA, "proyectos": PROYECTOS[:1] * (MAX_PROYECTOS + 1)},
    {"habilidades": ALUMNO_JAVA, "proyectos": PROYECTOS, "limite": 0},
    {"habilidades": ALUMNO_JAVA, "proyectos": PROYECTOS, "campo_extra": 1},
    {"habilidades": ALUMNO_JAVA, "proyectos": [{"titulo": "Sin id", "habilidades": ["Java"]}]},
])
def test_entrada_invalida_devuelve_422(cliente, cuerpo):
    assert cliente.post(f"{URL}/proyectos", json=cuerpo).status_code == 422


def test_sin_modelo_devuelve_503(cliente):
    estado = cliente.app.state
    recomendador = estado.recomendador
    estado.recomendador = None
    try:
        assert cliente.post(f"{URL}/perfil", json={"habilidades": ALUMNO_JAVA}).status_code == 503
        salud = cliente.get(f"{PREFIJO}/salud")
        assert salud.status_code == 503
        assert salud.json()["estado"] == "degradado"
    finally:
        estado.recomendador = recomendador


#--- Clave entre servicios ---

@pytest.fixture
def con_api_key(cliente):
    cliente.app.dependency_overrides[obtener_configuracion] = lambda: replace(obtener_configuracion(), api_key="secreto")
    yield
    cliente.app.dependency_overrides.clear()


def test_api_key_requerida_cuando_esta_configurada(cliente, con_api_key):
    cuerpo = {"habilidades": ALUMNO_JAVA}
    assert cliente.post(f"{URL}/perfil", json=cuerpo).status_code == 401
    assert cliente.post(f"{URL}/perfil", json=cuerpo, headers={"X-API-Key": "incorrecta"}).status_code == 401
    assert cliente.post(f"{URL}/perfil", json=cuerpo, headers={"X-API-Key": "secreto"}).status_code == 200


def test_salud_no_requiere_api_key(cliente, con_api_key):
    assert cliente.get(f"{PREFIJO}/salud").status_code == 200
