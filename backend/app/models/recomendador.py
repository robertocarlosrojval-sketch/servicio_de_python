"""Modelo: acceso al recomendador entrenado.

Encapsula la carga del archivo .pkl (generado en entrenamiento_modelo.ipynb) y
expone tres operaciones: afinidad con proyectos, habilidades sugeridas y perfil
profesional. Recibe siempre nombres de habilidades ya normalizados.
"""
import json
import logging
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import sklearn
from sklearn.preprocessing import normalize

logger = logging.getLogger(__name__)


def _a_denso(matriz) -> np.ndarray:
    return matriz.toarray() if hasattr(matriz, "toarray") else np.asarray(matriz)


class Recomendador:
    def __init__(self, componentes: dict[str, Any], metadatos: dict[str, Any]):
        self._c = componentes
        self._metadatos = metadatos
        self._indice = {habilidad: i for i, habilidad in enumerate(componentes["vocabulario"].classes_)}

    @classmethod
    def cargar(cls, ruta_modelo: Path, ruta_metadatos: Path) -> "Recomendador":
        """Carga el modelo y sus metadatos desde disco.

        Solo se deben cargar archivos .pkl de confianza: pickle puede ejecutar
        codigo al deserializar.
        """
        for ruta in (ruta_modelo, ruta_metadatos):
            if not ruta.is_file():
                raise FileNotFoundError(f"No se encontró el archivo: {ruta}")

        with open(ruta_modelo, "rb") as archivo:
            componentes = pickle.load(archivo)
        with open(ruta_metadatos, encoding="utf-8") as archivo:
            metadatos = json.load(archivo)

        #Un .pkl solo es fiable con la misma version de scikit-learn que lo creo
        version_entrenamiento = metadatos.get("version_sklearn")
        if version_entrenamiento != sklearn.__version__:
            logger.warning(
                "El modelo se entrenó con scikit-learn %s, pero está instalada la %s",
                version_entrenamiento, sklearn.__version__,
            )

        return cls(componentes, metadatos)

    @property
    def metadatos(self) -> dict[str, Any]:
        return self._metadatos

    def conoce(self, habilidad: str) -> bool:
        return habilidad in self._indice

    def _vectorizar(self, listas: list[list[str]]):
        conocidas = [[h for h in lista if h in self._indice] for lista in listas]
        return self._c["vocabulario"].transform(conocidas).astype(float)

    def _representar(self, X):
        #Representacion elegida en el entrenamiento para el emparejamiento (TF-IDF + LSA)
        tfidf = self._c["tfidf"].transform(X)
        svd = self._c["svd"]
        return normalize(svd.transform(tfidf) if svd is not None else tfidf)

    def afinidades(self, habilidades_alumno: list[str], habilidades_proyectos: list[list[str]]) -> list[float]:
        """Similitud (0 a 1) entre el alumno y cada proyecto."""
        alumno = self._representar(self._vectorizar([habilidades_alumno]))
        proyectos = self._representar(self._vectorizar(habilidades_proyectos))
        similitud = _a_denso(alumno @ proyectos.T).ravel()
        return np.clip(similitud, 0, 1).tolist()

    def sugerir_habilidades(self, habilidades: list[str], limite: int) -> list[tuple[str, str, float]]:
        """Habilidades que piden las vacantes mas parecidas al alumno y que el alumno no tiene.

        Devuelve (habilidad, categoria, relevancia), con la relevancia relativa a la primera (1.0).
        """
        X = self._vectorizar([habilidades])
        if self._c["rep_sugerencias"] == "TF-IDF":
            consulta = normalize(self._c["tfidf"].transform(X))
        else:
            consulta = self._representar(X)

        similitud = _a_denso(consulta @ self._c["vacantes_referencia"].T).ravel()
        vecinos = np.argsort(-similitud)[: self._c["k_vecinos"]]
        puntajes = similitud[vecinos] @ self._c["vacantes_binaria"][vecinos].toarray()
        puntajes[[self._indice[h] for h in habilidades if h in self._indice]] = 0

        mejores = [i for i in np.argsort(-puntajes)[:limite] if puntajes[i] > 0]
        if not mejores:
            return []
        maximo = puntajes[mejores[0]]
        clases = self._c["vocabulario"].classes_
        return [
            (clases[i], self._c["categorias"].get(clases[i], "Sin clasificar"), round(float(puntajes[i] / maximo), 4))
            for i in mejores
        ]

    def perfil(self, habilidades: list[str]) -> tuple[str, list[str]]:
        """Perfil profesional mas cercano y sus habilidades clave."""
        X = self._vectorizar([habilidades])
        z = normalize(self._c["svd_perfiles"].transform(self._c["tfidf_perfiles"].transform(X)))
        grupo = int(self._c["kmeans"].predict(z)[0])
        info = self._c["perfiles"][grupo]
        return info["perfil"], list(info["habilidades_clave"])
