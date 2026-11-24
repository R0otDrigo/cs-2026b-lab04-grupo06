"""Datos FICTICIOS de la flota para el servidor MCP de RutaSIT (no son posiciones reales).

Cada ruta tiene un trazado [(lat, lon), ...] y sus paraderos ubicados por kilómetro recorrido, que es
lo que usa rutasit.llegada (HU-01). Las posiciones de los buses salen del trazado, salvo la del bus
V2B-789, que corta la curva de la R-07 por dentro (el caso del issue #3).
"""
import math

from rutasit.gps import Posicion

_M_POR_GRADO_LAT = 110_540.0
_M_POR_GRADO_LON = 111_320.0


def _largo_m(a, b):
    dy = (b[0] - a[0]) * _M_POR_GRADO_LAT
    dx = (b[1] - a[1]) * _M_POR_GRADO_LON * math.cos(math.radians(a[0]))
    return math.hypot(dx, dy)


def punto_en_km(trazado, km):
    """Punto (lat, lon) del trazado a 'km' kilómetros del inicio (interpolación por tramos)."""
    resto = km * 1000
    for a, b in zip(trazado, trazado[1:]):
        largo = _largo_m(a, b)
        if resto <= largo:
            t = resto / largo
            return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        resto -= largo
    return trazado[-1]


RUTAS = {
    "R-07": {
        "nombre": "Cerro Colorado - Centro",
        "trazado": [(-16.4090, -71.5375), (-16.4090, -71.5188), (-16.3909, -71.5188)],   # forma de "L"
        "paraderos": {"Terminal Cerro Colorado": 0.0, "Av. Ejército": 1.0, "Puente Grau": 2.0,
                      "Plaza de Armas": 4.0},
    },
    "R-12": {
        "nombre": "Yanahuara - Mercado San Camilo",
        "trazado": [(-16.3880, -71.5450), (-16.3960, -71.5400), (-16.4020, -71.5330)],
        "paraderos": {"Mirador de Yanahuara": 0.0, "Av. Ejército": 1.0, "Mercado San Camilo": 2.0},
    },
}

# placa, operador, ruta, km recorridos, velocidad (km/h). Las dos últimas posiciones se calculan abajo.
_BUSES = [
    ("V1A-123", "A", "R-07", 1.4, 24.0),
    ("V1A-456", "A", "R-07", 3.1, 20.0),
    ("V2B-789", "B", "R-07", 2.6, 18.0),
    ("V1A-321", "A", "R-12", 0.8, 22.0),
    ("V2B-654", "B", "R-12", 1.7, 25.0),
]
_POSICIONES_FUERA_DE_RUTA = {"V2B-789": [(-16.4018, -71.5300), (-16.4009, -71.5291)]}


def _posiciones(placa, ruta, km, vel):
    if placa in _POSICIONES_FUERA_DE_RUTA:
        return [Posicion(lat, lon, vel) for lat, lon in _POSICIONES_FUERA_DE_RUTA[placa]]
    trazado = RUTAS[ruta]["trazado"]
    return [Posicion(*punto_en_km(trazado, max(0.0, km - 0.03)), vel), Posicion(*punto_en_km(trazado, km), vel)]


BUSES = [
    {"placa": p, "operador": o, "ruta": r, "km": km, "vel_kmh": v, "posiciones": _posiciones(p, r, km, v)}
    for p, o, r, km, v in _BUSES
]
