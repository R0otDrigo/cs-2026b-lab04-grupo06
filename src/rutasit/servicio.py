from datetime import datetime

from .dominio import Estimacion, Paradero, Viaje
from .puertos import ProveedorMapas, RepositorioViajes


class ServicioAlertas:
    def __init__(self) -> None:
        self.avisos: list[str] = []

    def avisar_sin_senal(self, v: Viaje) -> None:
        self.avisos.append(f"SIN_SENAL:{v.id}")

    def avisar_desvio(self, v: Viaje) -> None:
        self.avisos.append(f"DESVIO:{v.id}")


class ServicioEta:
    def __init__(self, repositorio: RepositorioViajes, mapas: ProveedorMapas,
                 alertas: ServicioAlertas) -> None:
        self.repositorio = repositorio
        self.mapas = mapas
        self.alertas = alertas

    def consultar_eta(self, paradero: Paradero, ahora: datetime) -> Estimacion:
        viajes = self.repositorio.buscar_activos_por_paradero(paradero)
        con_senal = [v for v in viajes if not v.esta_sin_senal(ahora)]
        if con_senal:
            posicion = con_senal[0].ultima_posicion()
            minutos = self.mapas.tiempo_de_recorrido(posicion, paradero)
            return Estimacion(paradero, ahora, True, minutos)
        for v in viajes:
            self.alertas.avisar_sin_senal(v)
        return Estimacion(paradero, ahora, False, None)
