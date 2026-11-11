import pytest


@pytest.fixture(scope="module")
def normalizador(cliente):
    return cliente.app.state.normalizador


@pytest.mark.parametrize("texto, esperado", [
    ("Java", "Java"),
    ("  java ", "Java"),
    ("reactjs", "React"),
    ("React.js", "React"),
    ("NodeJS", "Node.js"),
    ("Golang", "Go"),
    ("Microsoft Azure", "Azure"),
    ("RESTful APIs", "REST API"),
    ("k8s", "Kubernetes"),
    ("javascript", "JavaScript"),
])
def test_variantes_se_normalizan(normalizador, texto, esperado):
    assert normalizador.nombre_canonico(texto) == esperado


def test_normalizar_quita_duplicados_y_separa_desconocidas(normalizador):
    reconocidas, no_reconocidas = normalizador.normalizar(["React", "reactjs", "Tecnologia Inventada", "Python"])
    assert reconocidas == ["React", "Python"]
    assert no_reconocidas == ["Tecnologia Inventada"]
