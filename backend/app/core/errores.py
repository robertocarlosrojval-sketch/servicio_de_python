"""Errores de negocio.

Los controladores lanzan estas excepciones sin saber nada de HTTP; main.py las
convierte en respuestas con el codigo de estado adecuado.
"""


class SinHabilidadesTecnicasError(Exception):
    """El alumno no tiene ninguna habilidad tecnica que el modelo reconozca."""

    def __init__(self, habilidades_no_reconocidas: list[str]):
        self.habilidades_no_reconocidas = habilidades_no_reconocidas
        super().__init__(
            "Ninguna de las habilidades del alumno es una habilidad técnica reconocida por el modelo."
        )
