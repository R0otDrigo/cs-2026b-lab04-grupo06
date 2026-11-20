from abc import ABC, abstractmethod

from .dominio import Paradero, Posicion, Viaje


class ProveedorMapas(ABC):
    """Puerto hacia el servicio externo de mapas (ADR-001: puertos y adaptadores)."""

    @abstractmethod
    def tiempo_de_recorrido(self, desde: Posicion, hasta: Paradero) -> int:
        """Minutos estimados para ir de la posición al paradero."""


class RepositorioViajes(ABC):
    @abstractmethod
    def buscar_activos_por_paradero(self, paradero: Paradero) -> list[Viaje]:
        """Viajes activos que pasan por el paradero, del más cercano al más lejano."""
