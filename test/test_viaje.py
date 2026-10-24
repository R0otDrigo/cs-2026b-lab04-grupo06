from datetime import datetime, timedelta

import pytest

from rutasit.dominio import (Bus, EstadoViaje, Paradero, Posicion, Ruta, Viaje)
from rutasit.servicios import ServicioAlertas, ServicioEta
from rutasit.puertos import ProveedorMapas, RepositorioViajes


def nuevo_viaje():
    p1, p2 = Paradero("A", -16.40, -71.53), Paradero("B", -16.41, -71.52)
    ruta = Ruta("R1", "Ruta 1", [p1, p2])
    return Viaje(Bus("ABC-123"), ruta, datetime(2026, 10, 10, 6, 0)), p2


def en_ruta():
    v, p = nuevo_viaje()
    v.iniciar()
    return v, p


def test_programar():
    v, _ = nuevo_viaje(); v.programar()
    assert v.estado == EstadoViaje.PROGRAMADO

def test_iniciar():
    v, _ = nuevo_viaje(); v.iniciar()
    assert v.estado == EstadoViaje.EN_RUTA

def test_marcar_desviado():
    v, _ = en_ruta(); v.marcar_desviado()
    assert v.estado == EstadoViaje.DESVIADO

def test_reanudar_desde_desviado():
    v, _ = en_ruta(); v.marcar_desviado(); v.reanudar()
    assert v.estado == EstadoViaje.EN_RUTA

def test_marcar_detenido():
    v, _ = en_ruta(); v.marcar_detenido()
    assert v.estado == EstadoViaje.DETENIDO

def test_reanudar_desde_detenido():
    v, _ = en_ruta(); v.marcar_detenido(); v.reanudar()
    assert v.estado == EstadoViaje.EN_RUTA

def test_finalizar_desde_en_ruta():
    v, _ = en_ruta(); v.finalizar()
    assert v.estado == EstadoViaje.FINALIZADO

def test_finalizar_desde_desviado():
    v, _ = en_ruta(); v.marcar_desviado(); v.finalizar()
    assert v.estado == EstadoViaje.FINALIZADO

def test_finalizar_desde_detenido():
    v, _ = en_ruta(); v.marcar_detenido(); v.finalizar()
    assert v.estado == EstadoViaje.FINALIZADO


def test_transicion_invalida():
    v, _ = nuevo_viaje()
    with pytest.raises(ValueError):
        v.finalizar()

def test_ruta_con_un_solo_paradero_falla():
    with pytest.raises(ValueError):
        Ruta("R2", "Ruta 2", [Paradero("A", 0, 0)])


class MapasFalso(ProveedorMapas):
    def tiempo_de_recorrido(self, desde, hasta):
        return 7

class RepoFalso(RepositorioViajes):
    def __init__(self, viajes): self.viajes = viajes
    def buscar_activos_por_paradero(self, paradero): return self.viajes

def test_eta_con_senal():
    v, p = en_ruta(); ahora = datetime(2026, 10, 10, 6, 5)
    v.registrar_posicion(Posicion(-16.4, -71.5, ahora - timedelta(seconds=10), 30))
    est = ServicioEta(RepoFalso([v]), MapasFalso(), ServicioAlertas()).consultar_eta(p, ahora)
    assert est.disponible and est.minutos == 7

def test_eta_sin_senal_avisa_al_operador():
    v, p = en_ruta(); ahora = datetime(2026, 10, 10, 6, 5)
    v.registrar_posicion(Posicion(-16.4, -71.5, ahora - timedelta(seconds=45), 30))
    alertas = ServicioAlertas()
    est = ServicioEta(RepoFalso([v]), MapasFalso(), alertas).consultar_eta(p, ahora)
    assert not est.disponible and len(alertas.avisos) == 1
