"""Issue #1: el GPS del operador A sin datos no debe tumbar el servicio de ETA."""
import pytest

from rutasit.gps import AdaptadorGpsA
from rutasit.servicio import ServicioEta, Viaje


class SdkSinDatos:
    def __init__(self, respuesta):
        self.respuesta = respuesta

    def leer_posicion(self, placa):
        return self.respuesta


@pytest.mark.parametrize("respuesta", [None, {}, {"lat": -16.40, "lon": -71.53}])
def test_issue_01_adaptador_devuelve_none_sin_datos(respuesta):
    assert AdaptadorGpsA(SdkSinDatos(respuesta)).leer("V1A-123") is None


def test_issue_01_servicio_responde_eta_no_disponible():
    servicio = ServicioEta(gps_a=SdkSinDatos(None))
    viaje = Viaje("V-07", "V1A-123", "A", "EN_RUTA")
    estimacion = servicio.consultar_eta(viaje, "Plaza de Armas")
    assert estimacion.disponible is False
    assert "alerta:V-07:sin senal" in servicio.eventos
