from .dominio import Paradero, Posicion
from .puertos import ProveedorMapas


class OsmAdapter(ProveedorMapas):
    def tiempo_de_recorrido(self, desde: Posicion, hasta: Paradero) -> int:
        raise NotImplementedError("Integrar con el proveedor de mapas")
