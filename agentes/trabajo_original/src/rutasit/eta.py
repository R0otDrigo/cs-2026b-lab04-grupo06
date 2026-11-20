"""Calculo del ETA: Strategy + Adapter + Decorator + Factory (registro)."""
from abc import ABC, abstractmethod


class ProveedorMapas(ABC):
    @abstractmethod
    def tiempo_de_recorrido(self, origen, destino) -> int:
        """Segundos de recorrido."""


class OsmAdapter(ProveedorMapas):
    def __init__(self, sdk):
        self._sdk = sdk

    def tiempo_de_recorrido(self, origen, destino):
        return self._sdk.route_seconds(origen, destino)


class EstrategiaEta(ABC):
    """STRATEGY: cada algoritmo de ETA es intercambiable."""

    @abstractmethod
    def estimar(self, pos, paradero: str) -> int:
        """Minutos hasta el paradero."""


class EtaPorVelocidad(EstrategiaEta):
    def estimar(self, pos, paradero):
        return round(1.0 * 60 / max(pos.vel_kmh, 5.0))


class EtaPorMapas(EstrategiaEta):
    def __init__(self, mapas: ProveedorMapas):
        self._mapas = mapas

    def estimar(self, pos, paradero):
        return round(self._mapas.tiempo_de_recorrido((pos.lat, pos.lon), paradero) / 60)


# ---------- DECORATORS ----------
class ConReintentosEta(EstrategiaEta):
    def __init__(self, interna: EstrategiaEta, intentos: int = 3):
        self._interna, self._intentos = interna, intentos

    def estimar(self, pos, paradero):
        for i in range(self._intentos):
            try:
                return self._interna.estimar(pos, paradero)
            except TimeoutError:
                if i == self._intentos - 1:
                    raise


class ConCacheEta(EstrategiaEta):
    """Solo guarda respuestas EXITOSAS (si la interna falla, nada se guarda)."""

    def __init__(self, interna: EstrategiaEta):
        self._interna, self._cache = interna, {}

    def estimar(self, pos, paradero):
        clave = (round(pos.lat, 3), round(pos.lon, 3), paradero)
        if clave not in self._cache:
            self._cache[clave] = self._interna.estimar(pos, paradero)
        return self._cache[clave]


class ConRespaldo(EstrategiaEta):
    """Si la principal agota sus reintentos, usa la estrategia de respaldo."""

    def __init__(self, principal: EstrategiaEta, respaldo: EstrategiaEta):
        self._principal, self._respaldo = principal, respaldo

    def estimar(self, pos, paradero):
        try:
            return self._principal.estimar(pos, paradero)
        except TimeoutError:
            return self._respaldo.estimar(pos, paradero)


# ---------- FACTORY (registro) ----------
class FabricaEta:
    def __init__(self):
        self._creadores = {}

    def registrar(self, nombre: str, creador):
        self._creadores[nombre] = creador

    def crear(self, nombre: str) -> EstrategiaEta:
        if nombre not in self._creadores:
            raise ValueError(f"Algoritmo de ETA no soportado: {nombre}")
        return self._creadores[nombre]()
