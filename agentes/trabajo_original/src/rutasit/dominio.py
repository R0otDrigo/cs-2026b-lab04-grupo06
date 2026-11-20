from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

SEGUNDOS_SIN_SENAL = 30


class EstadoViaje(Enum):
    PROGRAMADO = "PROGRAMADO"
    EN_RUTA = "EN_RUTA"
    DESVIADO = "DESVIADO"
    DETENIDO = "DETENIDO"
    FINALIZADO = "FINALIZADO"


@dataclass
class Paradero:
    nombre: str
    latitud: float
    longitud: float
    id: UUID = field(default_factory=uuid4)


@dataclass
class Ruta:
    codigo: str
    nombre: str
    paraderos: list[Paradero] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        # Multiplicidad 2..* del diagrama (regla C3): una ruta tiene al menos 2 paraderos.
        if len(self.paraderos) < 2:
            raise ValueError("Una ruta necesita al menos 2 paraderos")


@dataclass
class Bus:
    placa: str
    id: UUID = field(default_factory=uuid4)


@dataclass
class Posicion:
    latitud: float
    longitud: float
    instante: datetime
    velocidad_kmh: float


@dataclass
class Estimacion:
    paradero: Paradero
    calculada_en: datetime
    disponible: bool
    minutos: int | None = None


@dataclass
class Viaje:
    bus: Bus
    ruta: Ruta
    hora_salida: datetime
    estado: EstadoViaje = EstadoViaje.PROGRAMADO
    posiciones: list[Posicion] = field(default_factory=list)
    id: UUID = field(default_factory=uuid4)

    def _exigir(self, *permitidos: EstadoViaje) -> None:
        if self.estado not in permitidos:
            raise ValueError(f"No se puede hacer esto desde el estado {self.estado.value}")

    def programar(self) -> None:
        self.estado = EstadoViaje.PROGRAMADO

    def iniciar(self) -> None:
        self._exigir(EstadoViaje.PROGRAMADO)
        self.estado = EstadoViaje.EN_RUTA

    def registrar_posicion(self, p: Posicion) -> None:
        self._exigir(EstadoViaje.EN_RUTA, EstadoViaje.DESVIADO, EstadoViaje.DETENIDO)
        self.posiciones.append(p)

    def ultima_posicion(self) -> Posicion | None:
        return self.posiciones[-1] if self.posiciones else None

    def esta_sin_senal(self, ahora: datetime) -> bool:
        ultima = self.ultima_posicion()
        if ultima is None:
            return True
        return (ahora - ultima.instante).total_seconds() > SEGUNDOS_SIN_SENAL

    def marcar_desviado(self) -> None:
        self._exigir(EstadoViaje.EN_RUTA)
        self.estado = EstadoViaje.DESVIADO

    def marcar_detenido(self) -> None:
        self._exigir(EstadoViaje.EN_RUTA)
        self.estado = EstadoViaje.DETENIDO

    def reanudar(self) -> None:
        self._exigir(EstadoViaje.DESVIADO, EstadoViaje.DETENIDO)
        self.estado = EstadoViaje.EN_RUTA

    def finalizar(self) -> None:
        self._exigir(EstadoViaje.EN_RUTA, EstadoViaje.DESVIADO, EstadoViaje.DETENIDO)
        self.estado = EstadoViaje.FINALIZADO
