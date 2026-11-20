"""Pruebas de caracterizacion: las MISMAS pruebas corren sobre antes y despues."""
import importlib

import pytest

from rutasit.externos import GpsOperadorA, GpsOperadorB, MapasOSM, ClienteLLMFalso


@pytest.fixture(params=["rutasit.antes.servicio", "rutasit.servicio"])
def m(request):
    return importlib.import_module(request.param)


def viaje(m, operador="A", estado="EN_RUTA"):
    return m.Viaje(id=1, placa="ABC-123", operador=operador, estado=estado)


def test_eta_por_mapas_publica_eventos(m):
    s = m.ServicioEta()
    est = s.consultar_eta(viaje(m), "Plaza")
    assert (est.minutos, est.disponible) == (5, True)
    assert s.eventos == ["pasajero:Plaza:llega en 5 min"]


def test_eta_por_velocidad(m):
    s = m.ServicioEta(gps_a=GpsOperadorA(vel_kmh=30.0))
    assert s.consultar_eta(viaje(m), "Plaza", "VELOCIDAD").minutos == 2


def test_gps_reintenta_tras_dos_timeouts(m):
    gps = GpsOperadorA(fallas=2)
    est = m.ServicioEta(gps_a=gps).consultar_eta(viaje(m), "Plaza")
    assert est.disponible and gps.llamadas == 3


def test_sin_senal_tras_tres_timeouts(m):
    s = m.ServicioEta(gps_a=GpsOperadorA(fallas=3))
    est = s.consultar_eta(viaje(m), "Plaza")
    assert (est.minutos, est.disponible) == (0, False)
    assert s.eventos == ["alerta:1:sin senal"]


def test_operador_b_convierte_unidades(m):
    # 5 m/s = 18 km/h -> 60/18 = 3,33 -> 3 min
    s = m.ServicioEta(gps_b=GpsOperadorB(vel_ms=5.0))
    assert s.consultar_eta(viaje(m, "B"), "Plaza", "VELOCIDAD").minutos == 3


def test_operador_b_codigo_distinto_de_200_no_reintenta(m):
    gps = GpsOperadorB(codigo=500)
    s = m.ServicioEta(gps_b=gps)
    assert s.consultar_eta(viaje(m, "B"), "Plaza").disponible is False
    assert gps.llamadas == 1


def test_retraso_publica_alerta(m):
    s = m.ServicioEta(mapas=MapasOSM(segundos=1500))
    assert s.consultar_eta(viaje(m), "Plaza").minutos == 25
    assert s.eventos == ["pasajero:Plaza:llega en 25 min", "alerta:1:retraso"]


def test_cache_evita_llamadas_repetidas_a_mapas(m):
    mapas = MapasOSM()
    s = m.ServicioEta(mapas=mapas)
    s.consultar_eta(viaje(m), "Plaza")
    s.consultar_eta(viaje(m), "Plaza")
    assert mapas.llamadas == 1


def test_mapas_caido_usa_velocidad_y_no_guarda_en_cache(m):
    mapas = MapasOSM(fallas=3)
    s = m.ServicioEta(mapas=mapas)
    assert s.consultar_eta(viaje(m), "Plaza").minutos == 2   # respaldo por velocidad
    assert s.consultar_eta(viaje(m), "Plaza").minutos == 5   # mapas ya responde
    assert mapas.llamadas == 4


def test_transiciones_invalidas_para_consultar(m):
    esperado = {"PROGRAMADO": "El viaje aun no inicia",
                "FINALIZADO": "El viaje ya finalizo",
                "DESVIADO": "Estado no valido"}
    for estado, mensaje in esperado.items():
        with pytest.raises(ValueError, match=mensaje):
            m.ServicioEta().consultar_eta(viaje(m, estado=estado), "Plaza")


def test_operador_no_soportado(m):
    with pytest.raises(ValueError, match="Operador GPS no soportado"):
        m.ServicioEta().consultar_eta(viaje(m, "Z"), "Plaza")


def test_algoritmo_no_soportado_no_consume_el_gps(m):
    if m.__name__.startswith("rutasit.antes"):
        pytest.xfail("BUG de antes: lee el GPS y guarda la posicion antes de validar el algoritmo")
    gps = GpsOperadorA()
    v = viaje(m)
    with pytest.raises(ValueError, match="Algoritmo de ETA no soportado"):
        m.ServicioEta(gps_a=gps).consultar_eta(v, "Plaza", "MAGIA")
    assert gps.llamadas == 0 and v.posiciones == []


def test_ia_texto_valido_pasa(m):
    s = m.ServicioEta(llm=ClienteLLMFalso("Hubo trafico en la Av. Ejercito."))
    assert s.sugerir_explicacion_retraso(["alerta:1:retraso"]) == "Hubo trafico en la Av. Ejercito."


def test_ia_guardrails_bloquean_salidas_invalidas(m):
    casos = {"El pasaje cuesta S/ 1.50": "precio",
             "Llegara a tiempo, garantizado": "afirmacion no permitida",
             "x" * 300: "demasiado largo"}
    for texto, mensaje in casos.items():
        s = m.ServicioEta(llm=ClienteLLMFalso(texto))
        with pytest.raises(ValueError, match=mensaje):
            s.sugerir_explicacion_retraso(["alerta:1:retraso"])
