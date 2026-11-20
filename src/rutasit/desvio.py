"""Deteccion de desvios (RF-04).

Un bus esta desviado si esta a mas de 150 m del trazado de la ruta en dos
posiciones seguidas. Las coordenadas se pasan a metros con una proyeccion
plana local, suficiente para distancias de una ciudad.
"""
import math

UMBRAL_DESVIO_M = 150.0
_M_POR_GRADO_LAT = 110_540.0
_M_POR_GRADO_LON_ECUADOR = 111_320.0


def _a_metros(lat, lon, lat_ref):
    x = lon * _M_POR_GRADO_LON_ECUADOR * math.cos(math.radians(lat_ref))
    y = lat * _M_POR_GRADO_LAT
    return x, y


def _distancia_punto_segmento(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    largo2 = dx * dx + dy * dy
    t = 0.0 if largo2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / largo2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def distancia_a_ruta(pos, trazado):
    """Metros entre la posicion del bus y el trazado [(lat, lon), ...] de la ruta."""
    lat_ref = trazado[0][0]
    p = _a_metros(pos.lat, pos.lon, lat_ref)
    puntos = [_a_metros(lat, lon, lat_ref) for lat, lon in trazado]
    # Tramo mas cercano: en una curva la recta inicio-fin no representa la ruta (RF-04).
    return min(_distancia_punto_segmento(p, a, b) for a, b in zip(puntos, puntos[1:]))


def hay_desvio(posiciones, trazado) -> bool:
    """True si las dos ultimas posiciones estan a mas de 150 m del trazado."""
    ultimas = posiciones[-2:]
    return len(ultimas) == 2 and all(distancia_a_ruta(p, trazado) > UMBRAL_DESVIO_M for p in ultimas)
