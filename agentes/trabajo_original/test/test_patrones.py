"""Pruebas que demuestran cada patron (solo sobre la version con patrones)."""
import pytest

from rutasit import servicio as sv
from rutasit.estados import Programado, EnRuta
from rutasit.eta import EstrategiaEta, EtaPorMapas, EtaPorVelocidad, ConCacheEta, ConRespaldo, OsmAdapter
from rutasit.eventos import Suscriptor
from rutasit.externos import GpsOperadorA, GpsOperadorB, MapasOSM, ClienteLLMFalso
from rutasit.gps import AdaptadorGpsB, ConReintentos, PuertoGps, Posicion
from rutasit.ia import Guardrail, SinPrecios, cadena_por_defecto


def viaje(estado="EN_RUTA", operador="A"):
    return sv.Viaje(1, "ABC-123", operador, estado)


# ---------- Strategy + Factory: abierto/cerrado ----------
def test_open_closed_nuevo_algoritmo_sin_modificar_el_servicio():
    class EtaFija(EstrategiaEta):
        def estimar(self, pos, paradero):
            return 7

    s = sv.ServicioEta()
    s.fabrica_eta.registrar("FIJO", EtaFija)          # solo se REGISTRA
    assert s.consultar_eta(viaje(), "Plaza", "FIJO").minutos == 7


def test_open_closed_nuevo_operador_gps_sin_modificar_el_servicio():
    class GpsC(PuertoGps):
        def leer(self, placa):
            return Posicion(-16.4, -71.5, 60.0)

    s = sv.ServicioEta()
    s.fabrica_gps.registrar("C", GpsC)
    assert s.consultar_eta(viaje(operador="C"), "Plaza", "VELOCIDAD").minutos == 1


def test_strategy_liskov_todas_las_estrategias_se_usan_igual():
    pos = Posicion(-16.4, -71.5, 30.0)
    for e in (EtaPorVelocidad(), EtaPorMapas(OsmAdapter(MapasOSM(segundos=600)))):
        assert isinstance(e.estimar(pos, "Plaza"), int)


# ---------- Adapter ----------
def test_adapter_traduce_formato_del_operador_b():
    p = AdaptadorGpsB(GpsOperadorB(vel_ms=10.0)).leer("ABC")
    assert (p.lat, p.lon, round(p.vel_kmh)) == (-16.4, -71.53, 36)


# ---------- Decorator ----------
def test_decorator_cache_evita_llamadas_repetidas():
    mapas = MapasOSM()
    e = ConCacheEta(EtaPorMapas(OsmAdapter(mapas)))
    pos = Posicion(-16.4, -71.5, 30.0)
    e.estimar(pos, "Plaza"); e.estimar(pos, "Plaza")
    assert mapas.llamadas == 1


def test_decorator_reintentos_no_reintenta_si_no_hay_timeout():
    gps = GpsOperadorB(codigo=500)
    assert ConReintentos(AdaptadorGpsB(gps)).leer("ABC") is None
    assert gps.llamadas == 1


def test_decorator_orden_importa_respaldo_no_se_guarda_en_cache():
    """Error tipico de la IA: poner el cache FUERA del respaldo guarda un ETA de emergencia."""
    pos = Posicion(-16.4, -71.5, 30.0)
    mapas = MapasOSM(fallas=1)
    mal = ConCacheEta(ConRespaldo(EtaPorMapas(OsmAdapter(mapas)), EtaPorVelocidad()))
    assert mal.estimar(pos, "Plaza") == 2 and mal.estimar(pos, "Plaza") == 2   # se quedo pegado
    mapas = MapasOSM(fallas=1)
    bien = ConRespaldo(ConCacheEta(EtaPorMapas(OsmAdapter(mapas))), EtaPorVelocidad())
    assert bien.estimar(pos, "Plaza") == 2 and bien.estimar(pos, "Plaza") == 5


# ---------- State ----------
def test_state_ciclo_valido_del_lab05():
    v = viaje("PROGRAMADO")
    v.iniciar(); v.marcar_desviado(); v.reanudar(); v.marcar_detenido(); v.reanudar(); v.finalizar()
    assert v.estado == "FINALIZADO"


def test_state_impide_transiciones_invalidas():
    for estado, accion in [("PROGRAMADO", "finalizar"), ("FINALIZADO", "iniciar"),
                           ("EN_RUTA", "reanudar"), ("DESVIADO", "marcar_detenido")]:
        v = viaje(estado)
        with pytest.raises(ValueError, match="No se puede"):
            getattr(v, accion)()
        assert v.estado == estado          # el estado no cambia


# ---------- Observer ----------
def test_observer_nuevo_suscriptor_sin_tocar_el_servicio():
    class Auditoria(Suscriptor):
        def __init__(self):
            self.registro = []

        def actualizar(self, evento, datos):
            self.registro.append((evento, datos["id"]))

    s, a = sv.ServicioEta(), Auditoria()
    s.publicador.suscribir("eta_calculado", a)
    s.consultar_eta(viaje(), "Plaza")
    assert a.registro == [("eta_calculado", 1)]


# ---------- IA aislada ----------
def test_ia_cache_evita_pagar_dos_veces_por_el_mismo_prompt():
    llm = ClienteLLMFalso("Hubo trafico.")
    s = sv.ServicioEta(llm=llm)
    s.sugerir_explicacion_retraso(["alerta:1:retraso"])
    s.sugerir_explicacion_retraso(["alerta:1:retraso"])
    assert llm.llamadas == 1


def test_chain_se_puede_extender_con_un_guardrail_nuevo():
    class SinUrls(Guardrail):
        def _aplicar(self, texto):
            if "http" in texto:
                raise ValueError("Guardrail: URL no permitida")
            return texto

    cadena = SinUrls(cadena_por_defecto())
    with pytest.raises(ValueError, match="URL"):
        cadena.validar("mira http://malo.com")
    assert cadena.validar("Hubo trafico.") == "Hubo trafico."


def test_chain_el_primero_que_falla_corta_la_cadena():
    with pytest.raises(ValueError, match="precio"):
        SinPrecios(cadena_por_defecto()).validar("S/ 2.50 garantizado")
