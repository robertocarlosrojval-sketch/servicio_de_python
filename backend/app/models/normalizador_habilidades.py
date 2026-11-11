"""Modelo: normalizacion de nombres de habilidades.

Convierte las habilidades tal como llegan desde la plataforma ("reactjs",
"Golang", "  java ") en los nombres canonicos que conoce el modelo ("React",
"Go", "Java"). Aplica las mismas reglas que inspeccion_limpieza.ipynb.
"""
import json
from pathlib import Path


class NormalizadorHabilidades:
    def __init__(self, sinonimos: dict[str, str], nombres: dict[str, str], categorias: dict[str, str]):
        self._sinonimos = sinonimos
        self._nombres = nombres
        self._categorias = categorias

    @classmethod
    def cargar(cls, ruta: Path) -> "NormalizadorHabilidades":
        if not ruta.is_file():
            raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return cls(datos["sinonimos"], datos["nombres"], datos["categorias"])

    @staticmethod
    def _clave(texto: str) -> str:
        clave = texto.strip().lower()
        for caracter in (" ", ".", "-", "_"):
            clave = clave.replace(caracter, "")
        #Quitar el sufijo "js" solo si queda algo antes (React.js -> react, pero "JS" se conserva)
        if clave.endswith("js") and len(clave) > 2:
            clave = clave[:-2]
        return clave

    def nombre_canonico(self, texto: str) -> str | None:
        clave = self._clave(texto)
        return self._nombres.get(self._sinonimos.get(clave, clave))

    def normalizar(self, habilidades: list[str]) -> tuple[list[str], list[str]]:
        """Devuelve (reconocidas, no_reconocidas), sin duplicados y en el orden recibido."""
        reconocidas, no_reconocidas = [], []
        for texto in habilidades:
            canonico = self.nombre_canonico(texto)
            if canonico is None:
                if texto.strip() not in no_reconocidas:
                    no_reconocidas.append(texto.strip())
            elif canonico not in reconocidas:
                reconocidas.append(canonico)
        return reconocidas, no_reconocidas

    def categoria(self, habilidad: str) -> str:
        return self._categorias.get(habilidad, "Sin clasificar")

    def catalogo(self) -> dict[str, str]:
        """Todas las habilidades conocidas con su categoria."""
        return dict(self._categorias)
