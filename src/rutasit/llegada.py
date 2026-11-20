"""Tiempo de llegada medido a lo largo de la ruta (HU-01).

Cada paradero y el bus se ubican por los kilometros recorridos desde el
inicio de la ruta. Con eso el ETA no depende de la distancia en linea recta.
"""
from rutasit.eta import EstrategiaEta

VELOCIDAD_MINIMA_KMH = 5.0


def minutos_hasta_paradero(km_bus: float, km_paradero: float, vel_kmh: float):
    """Minutos que faltan para que el bus llegue al paradero."""
    distancia_km = km_paradero - km_bus
    if distancia_km < 0:
        return None  # el bus ya paso el paradero: "ETA no disponible" (HU-01)
    return round(distancia_km / max(vel_kmh, VELOCIDAD_MINIMA_KMH) * 60)


class EtaPorRecorrido(EstrategiaEta):
    """STRATEGY: ETA segun el avance del bus sobre la ruta."""

    def __init__(self, km_de_paradero: dict, km_del_bus):
        self._km_de_paradero = km_de_paradero   # {"Plaza de Armas": 4.2, ...}
        self._km_del_bus = km_del_bus           # funcion: Posicion -> km recorridos

    def estimar(self, pos, paradero):
        return minutos_hasta_paradero(self._km_del_bus(pos), self._km_de_paradero[paradero], pos.vel_kmh)
