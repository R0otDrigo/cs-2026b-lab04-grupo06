"""Servicios externos SIMULADOS de RutaSIT (no hay red ni claves de API).

Cada operador de GPS entrega la posicion en un formato distinto, igual que en la
realidad. El proveedor de mapas tambien tiene su propia interfaz.
"""


class GpsOperadorA:
    """Operador A: JSON con lat/lon en grados y velocidad en km/h."""

    def __init__(self, fallas=0, vel_kmh=30.0):
        self.fallas, self.llamadas, self.vel_kmh = fallas, 0, vel_kmh

    def leer_posicion(self, placa):
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("GPS A sin respuesta")
        return {"lat": -16.40, "lon": -71.53, "vel_kmh": self.vel_kmh, "ok": True}


class GpsOperadorB:
    """Operador B: tupla (latE6, lonE6, velocidad en m/s, codigo HTTP)."""

    def __init__(self, fallas=0, codigo=200, vel_ms=5.0):
        self.fallas, self.llamadas = fallas, 0
        self.codigo, self.vel_ms = codigo, vel_ms

    def get_fix(self, id_bus):
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("GPS B sin respuesta")
        return (-16400000, -71530000, self.vel_ms, self.codigo)


class MapasOSM:
    """Proveedor de mapas: devuelve segundos de recorrido."""

    def __init__(self, fallas=0, segundos=300):
        self.fallas, self.llamadas, self.segundos = fallas, 0, segundos

    def route_seconds(self, origen, destino):
        self.llamadas += 1
        if self.llamadas <= self.fallas:
            raise TimeoutError("OSM sin respuesta")
        return self.segundos


class ClienteLLMFalso:
    """LLM simulado: devuelve exactamente la respuesta que se quiere probar."""

    def __init__(self, respuesta="El bus se retraso por trafico en la Av. Ejercito."):
        self.respuesta, self.llamadas = respuesta, 0

    def generate(self, prompt):
        self.llamadas += 1
        return self.respuesta
