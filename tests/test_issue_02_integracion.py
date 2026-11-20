"""Issue #2 (prueba agregada por el humano a pedido del revisor): consultar_eta con la estrategia
RECORRIDO cuando el bus ya pasó el paradero responde "ETA no disponible" sin publicar eventos."""
from rutasit.externos import GpsOperadorA
from rutasit.llegada import EtaPorRecorrido
from rutasit.servicio import ServicioEta, Viaje


def _servicio(km_bus):
    recorrido = EtaPorRecorrido({"Plaza de Armas": 2.0}, km_del_bus=lambda pos: km_bus)
    return ServicioEta(gps_a=GpsOperadorA(vel_kmh=30.0), recorrido=recorrido)


def test_issue_02_servicio_bus_que_ya_paso_no_tiene_eta():
    servicio = _servicio(km_bus=3.0)
    estimacion = servicio.consultar_eta(Viaje("V-09", "V1A-123", "A", "EN_RUTA"), "Plaza de Armas", "RECORRIDO")
    assert estimacion.disponible is False
    assert servicio.eventos == []


def test_issue_02_servicio_bus_antes_del_paradero():
    servicio = _servicio(km_bus=1.0)
    estimacion = servicio.consultar_eta(Viaje("V-09", "V1A-123", "A", "EN_RUTA"), "Plaza de Armas", "RECORRIDO")
    assert (estimacion.minutos, estimacion.disponible) == (2, True)
    assert "pasajero:Plaza de Armas:llega en 2 min" in servicio.eventos
