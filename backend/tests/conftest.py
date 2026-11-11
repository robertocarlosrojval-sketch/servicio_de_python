import pytest
from fastapi.testclient import TestClient

from app.main import app

PREFIJO = "/api/v1"

ALUMNO_JAVA = ["Java", "Spring Boot", "SQL", "Git", "HTML"]

PROYECTOS = [
    {"id": 1, "titulo": "Sistema de inventarios web",
     "habilidades": ["Java", "Spring Boot", "PostgreSQL", "REST API", "Docker"]},
    {"id": 2, "titulo": "Portal web institucional", "habilidades": ["HTML", "CSS", "JavaScript", "React"]},
    {"id": 3, "titulo": "Tablero de análisis de ventas",
     "habilidades": ["Python", "SQL", "Machine Learning", "Data Analysis"]},
    {"id": 4, "titulo": "Firmware para sensor IoT", "habilidades": ["C", "Embedded Systems", "RTOS", "I2C"]},
]


@pytest.fixture(scope="session")
def cliente():
    #El "with" ejecuta el ciclo de vida de la app, es decir, carga el modelo
    with TestClient(app) as cliente:
        yield cliente
