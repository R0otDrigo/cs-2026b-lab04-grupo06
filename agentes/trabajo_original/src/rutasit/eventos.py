"""Notificaciones: patron Observer."""
from abc import ABC, abstractmethod


class Suscriptor(ABC):
    @abstractmethod
    def actualizar(self, evento: str, datos: dict): ...


class PublicadorEventos:
    def __init__(self):
        self._suscriptores = {}

    def suscribir(self, evento: str, suscriptor: Suscriptor):
        self._suscriptores.setdefault(evento, []).append(suscriptor)

    def publicar(self, evento: str, datos: dict):
        for s in self._suscriptores.get(evento, []):
            s.actualizar(evento, datos)


class NotificadorPasajero(Suscriptor):
    def __init__(self, bandeja):
        self._bandeja = bandeja

    def actualizar(self, evento, datos):
        self._bandeja.append(f"pasajero:{datos['paradero']}:llega en {datos['minutos']} min")


class AlertaOperador(Suscriptor):
    def __init__(self, bandeja):
        self._bandeja = bandeja

    def actualizar(self, evento, datos):
        motivo = "retraso" if evento == "retraso_detectado" else "sin senal"
        self._bandeja.append(f"alerta:{datos['id']}:{motivo}")
