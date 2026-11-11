"""Controlador del catalogo de habilidades."""
from app.models.normalizador_habilidades import NormalizadorHabilidades
from app.schemas.habilidad import CatalogoSalida, HabilidadCatalogo


def listar_habilidades(
    normalizador: NormalizadorHabilidades, categoria: str | None, busqueda: str | None
) -> CatalogoSalida:
    habilidades = [
        HabilidadCatalogo(habilidad=habilidad, categoria=cat)
        for habilidad, cat in sorted(normalizador.catalogo().items(), key=lambda par: par[0].lower())
        if (categoria is None or cat == categoria)
        and (busqueda is None or busqueda.lower() in habilidad.lower())
    ]
    return CatalogoSalida(total=len(habilidades), habilidades=habilidades)
