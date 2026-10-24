"""VERSION DESPUES: el servicio solo coordina; los patrones hacen el trabajo."""
from rutasit.externos import GpsOperadorA, GpsOperadorB, MapasOSM, ClienteLLMFalso
from rutasit.gps import AdaptadorGpsA, AdaptadorGpsB, FabricaGps, Posicion
from rutasit.eta import (OsmAdapter, EtaPorMapas, EtaPorVelocidad, ConCacheEta,
                         ConReintentosEta, ConRespaldo, FabricaEta)
from rutasit.estados import ESTADOS, Programado
from rutasit.eventos import PublicadorEventos, NotificadorPasajero, AlertaOperador
from rutasit.ia import ClaudeAdapter, ConCacheLLM, cadena_por_defecto

LIMITE_RETRASO_MIN = 20


class Viaje:
    def __init__(self, id, placa, operador, estado="PROGRAMADO"):
        self.id, self.placa, self.operador = id, placa, operador
        self._estado = ESTADOS[estado]()
        self.posiciones = []

    @property
    def estado(self) -> str:
        return self._estado.nombre

    def cambiar_a(self, nuevo):
        self._estado = nuevo

    def iniciar(self): self._estado.iniciar(self)
    def marcar_desviado(self): self._estado.marcar_desviado(self)
    def marcar_detenido(self): self._estado.marcar_detenido(self)
    def reanudar(self): self._estado.reanudar(self)
    def finalizar(self): self._estado.finalizar(self)
    def verificar_eta(self): self._estado.verificar_eta(self)


class Estimacion:
    def __init__(self, minutos, disponible):
        self.minutos, self.disponible = minutos, disponible


class ServicioEta:
    def __init__(self, gps_a=None, gps_b=None, mapas=None, llm=None):
        gps_a, gps_b = gps_a or GpsOperadorA(), gps_b or GpsOperadorB()
        mapas, llm = mapas or MapasOSM(), llm or ClienteLLMFalso()
        self.fabrica_gps = FabricaGps()
        self.fabrica_gps.registrar("A", lambda: AdaptadorGpsA(gps_a))
        self.fabrica_gps.registrar("B", lambda: AdaptadorGpsB(gps_b))
        self.fabrica_eta = FabricaEta()
        proveedor = OsmAdapter(mapas)
        # el cache va DENTRO del respaldo: asi nunca guarda un ETA de emergencia
        mapas_robusto = ConRespaldo(
            ConCacheEta(ConReintentosEta(EtaPorMapas(proveedor))), EtaPorVelocidad())
        self.fabrica_eta.registrar("MAPAS", lambda: mapas_robusto)
        self.fabrica_eta.registrar("VELOCIDAD", EtaPorVelocidad)
        self.eventos = []
        self.publicador = PublicadorEventos()
        self.publicador.suscribir("eta_calculado", NotificadorPasajero(self.eventos))
        alerta = AlertaOperador(self.eventos)
        self.publicador.suscribir("retraso_detectado", alerta)
        self.publicador.suscribir("sin_senal", alerta)
        self.llm = ConCacheLLM(ClaudeAdapter(llm))
        self.guardrails = cadena_por_defecto()

    def consultar_eta(self, viaje, paradero, algoritmo="MAPAS"):
        viaje.verificar_eta()
        gps = self.fabrica_gps.crear(viaje.operador)
        estrategia = self.fabrica_eta.crear(algoritmo)
        pos = gps.leer(viaje.placa)
        if pos is None:
            self.publicador.publicar("sin_senal", {"id": viaje.id})
            return Estimacion(0, False)
        viaje.posiciones.append(pos)
        minutos = estrategia.estimar(pos, paradero)
        datos = {"id": viaje.id, "paradero": paradero, "minutos": minutos}
        self.publicador.publicar("eta_calculado", datos)
        if minutos > LIMITE_RETRASO_MIN:
            self.publicador.publicar("retraso_detectado", datos)
        return Estimacion(minutos, True)

    def sugerir_explicacion_retraso(self, eventos):
        prompt = "Explica el retraso: " + "; ".join(eventos)
        return self.guardrails.validar(self.llm.completar(prompt))
