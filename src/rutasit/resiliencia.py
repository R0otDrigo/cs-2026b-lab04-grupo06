"""Tactica de disponibilidad (Lab 08, ADR-007): circuit breaker como DECORATOR de una estrategia de ETA.

Se agrega sin modificar las estrategias ni los decoradores existentes (patrones del Lab 07)."""
import time

from rutasit.eta import EstrategiaEta


class CircuitoAbierto(TimeoutError):
    """Falla rapida: el proveedor esta caido. Es un TimeoutError para que ConRespaldo
    lo trate igual que una caida normal y use su ETA de respaldo."""


class ConCircuitBreakerEta(EstrategiaEta):
    def __init__(self, interna: EstrategiaEta, umbral=3, espera_s=30, reloj=time.monotonic):
        self._interna, self._umbral, self._espera, self._reloj = interna, umbral, espera_s, reloj
        self._fallas, self._abierto_desde = 0, None

    @property
    def estado(self) -> str:
        if self._abierto_desde is None:
            return "CERRADO"
        return "SEMIABIERTO" if self._reloj() - self._abierto_desde >= self._espera else "ABIERTO"

    def estimar(self, pos, paradero):
        if self.estado == "ABIERTO":
            raise CircuitoAbierto("Proveedor de mapas no disponible")
        try:
            minutos = self._interna.estimar(pos, paradero)
        except TimeoutError:
            self._registrar_falla()
            raise
        self._fallas, self._abierto_desde = 0, None  # exito: se cierra el circuito
        return minutos

    def _registrar_falla(self):
        self._fallas += 1
        if self._fallas >= self._umbral or self.estado == "SEMIABIERTO":
            self._abierto_desde = self._reloj()
