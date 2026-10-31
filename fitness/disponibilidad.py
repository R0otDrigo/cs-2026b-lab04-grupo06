"""Simulacion de disponibilidad de RutaSIT (Lab 08): el proveedor de mapas cae 20 minutos.

Usa las clases REALES del repositorio (rutasit.eta y rutasit.resiliencia) con un reloj simulado.
Supuestos (escritos aqui): 14 consultas/s, timeout del cliente = 2 s, respuesta normal del proveedor = 50 ms,
ETA por velocidad (respaldo) = 5 ms, caida de 20 min entre el minuto 10 y el 30 de una ventana de 40 min.
"""
import random

from rutasit.eta import (ConReintentosEta, ConRespaldo, EtaPorMapas, EtaPorVelocidad, ProveedorMapas)
from rutasit.gps import Posicion
from rutasit.resiliencia import ConCircuitBreakerEta

LAMBDA = 14               # consultas por segundo (hora punta)
VENTANA_S = 2400          # 40 minutos
CAIDA = (600, 1800)       # el proveedor cae entre el minuto 10 y el 30
TIMEOUT_S = 2.0
LATENCIA_OK_S = 0.05
LATENCIA_LOCAL_S = 0.005
POS = Posicion(lat=-16.40, lon=-71.53, vel_kmh=30.0)
VARIANTES = ["Sin tacticas", "Reintentos (3)", "Reintentos + respaldo", "Reintentos + respaldo + breaker"]


class ProveedorSimulado(ProveedorMapas):
    def __init__(self, estado):
        self.e = estado

    def tiempo_de_recorrido(self, origen, destino):
        e = self.e
        e["llamadas"] += 1
        if CAIDA[0] <= e["t"] < CAIDA[1]:
            e["llamadas_en_caida"] += 1
            e["consumido"] += TIMEOUT_S
            raise TimeoutError("el proveedor de mapas no responde")
        e["consumido"] += LATENCIA_OK_S
        return 300


def construir(variante, e):
    mapas = EtaPorMapas(ProveedorSimulado(e))
    respaldo = EtaPorVelocidad()
    if variante == "Sin tacticas":
        return mapas
    if variante == "Reintentos (3)":
        return ConReintentosEta(mapas, 3)
    if variante == "Reintentos + respaldo":
        return ConRespaldo(ConReintentosEta(mapas, 3), respaldo)
    return ConRespaldo(ConCircuitBreakerEta(ConReintentosEta(mapas, 3), umbral=3, espera_s=30,
                                            reloj=lambda: e["t"]), respaldo)


def simular(variante, semilla=11, lam=LAMBDA):
    rnd = random.Random(semilla)
    e = {"t": 0.0, "consumido": 0.0, "llamadas": 0, "llamadas_en_caida": 0}
    estrategia = construir(variante, e)
    t, lat_caida, por_minuto = 0.0, [], {}
    sin_eta, n_caida = 0, 0
    while True:
        t += rnd.expovariate(lam)
        if t >= VENTANA_S:
            break
        e["t"], e["consumido"] = t, 0.0
        try:
            estrategia.estimar(POS, "Paradero Selva Alegre")
            lat, ok = e["consumido"] + LATENCIA_LOCAL_S, True
        except TimeoutError:
            lat, ok = e["consumido"], False
        por_minuto.setdefault(int(t // 60), []).append(lat * 1000)
        if CAIDA[0] <= t < CAIDA[1]:
            n_caida += 1
            lat_caida.append(lat * 1000)
            sin_eta += 0 if ok else 1
    lat_caida.sort()
    p95 = lat_caida[int(0.95 * (len(lat_caida) - 1))]
    linea = [sorted(v)[int(0.95 * (len(v) - 1))] for _, v in sorted(por_minuto.items())]
    return {"consultas_en_caida": n_caida, "sin_eta": sin_eta, "p95_ms": p95,
            "llamadas_en_caida": e["llamadas_en_caida"], "p95_por_minuto": linea}
