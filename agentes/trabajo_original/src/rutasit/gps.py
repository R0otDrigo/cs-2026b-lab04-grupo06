"""Lectura de la posicion del bus: Adapter + Decorator + Factory (registro)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class Posicion:
    lat: float
    lon: float
    vel_kmh: float


class PuertoGps(ABC):
    """Puerto (interfaz) comun: todos los operadores de GPS se usan igual."""

    @abstractmethod
    def leer(self, placa: str) -> Posicion | None: ...


# ---------- ADAPTER: traduce cada SDK a la interfaz PuertoGps ----------
class AdaptadorGpsA(PuertoGps):
    def __init__(self, sdk):
        self._sdk = sdk

    def leer(self, placa):
        r = self._sdk.leer_posicion(placa)
        return Posicion(r["lat"], r["lon"], r["vel_kmh"])


class AdaptadorGpsB(PuertoGps):
    def __init__(self, sdk):
        self._sdk = sdk

    def leer(self, placa):
        lat, lon, vel_ms, codigo = self._sdk.get_fix(placa)
        if codigo != 200:
            return None
        return Posicion(lat / 1e6, lon / 1e6, vel_ms * 3.6)


# ---------- DECORATOR: reintentos sin modificar los adaptadores ----------
class ConReintentos(PuertoGps):
    def __init__(self, interno: PuertoGps, intentos: int = 3):
        self._interno, self._intentos = interno, intentos

    def leer(self, placa):
        for _ in range(self._intentos):
            try:
                return self._interno.leer(placa)
            except TimeoutError:
                continue
        return None


# ---------- FACTORY (registro): crea el adaptador segun el operador ----------
class FabricaGps:
    def __init__(self):
        self._creadores = {}

    def registrar(self, operador: str, creador):
        self._creadores[operador] = creador

    def crear(self, operador: str) -> PuertoGps:
        if operador not in self._creadores:
            raise ValueError(f"Operador GPS no soportado: {operador}")
        return ConReintentos(self._creadores[operador]())
