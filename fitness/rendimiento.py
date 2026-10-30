"""Simulacion de rendimiento de RutaSIT (Lab 08): la API como una cola M/G/c.

Llegadas de Poisson, c workers y tiempos de servicio lognormales. TODOS los tiempos de servicio son
SUPUESTOS (no se midieron con una prueba de carga real): estan escritos aqui, en un solo lugar, para
poder cambiarlos. Ver add/iteracion-1.md y el analisis de sensibilidad.
"""
import heapq
import math
import random
import statistics

# ---------------- Supuestos de carga (escenario de crecimiento, Tabla 11 de la guia) ----------------
BUSES = 1200
POSICIONES_POR_SEG = BUSES / 10          # cada bus envia su posicion cada 10 s (ADR-002) -> 120 pos/s
CONSULTAS_HORA_PUNTA = 50_000            # consultas de ETA en la hora punta (se asume 60 min)
CARGA_MEDIA = CONSULTAS_HORA_PUNTA / 3600  # 13,9 req/s
CARGAS_LECTURA = [("Normal\n5 req/s", 5), ("Hora punta\n14 req/s", 14), ("Rafaga x2\n28 req/s", 28)]
WORKERS = 4

# ---------------- Supuestos de servicio (mediana en ms, sigma de la lognormal) ----------------
def lognormal(mediana_ms, sigma):
    mu = math.log(mediana_ms / 1000.0)
    return lambda rnd: rnd.lognormvariate(mu, sigma)


# Ruta de LECTURA (consultar el ETA de un paradero)
bd_sin_indice = lognormal(250, 0.45)     # busca los viajes activos del paradero recorriendo la tabla
bd_con_indice = lognormal(35, 0.40)      # con indice espacial (GiST) y consulta acotada por ruta
redis_acierto = lognormal(4, 0.30)


def con_cache(servicio_base, tasa_aciertos=0.85):
    """CACHE de Redis (ADR-003). Un acierto responde desde memoria; un fallo va a la base de datos."""
    acierto = redis_acierto

    def f(rnd):
        return acierto(rnd) if rnd.random() < tasa_aciertos else servicio_base(rnd)
    return f


# Ruta de INGESTA (procesar la posicion que envia un bus)
escritura_pg = lognormal(8, 0.40)
eta_mapas = lognormal(60, 0.50)          # recalcular el ETA llamando al proveedor de mapas
eta_velocidad = lognormal(1, 0.30)       # recalcular el ETA con la velocidad del bus (EtaPorVelocidad)


def ingesta_hoy(rnd):
    return escritura_pg(rnd) + eta_mapas(rnd)


def ingesta_eta_hibrido(rnd, fraccion_mapas=0.10):
    """ETA por velocidad en el 90 % de las posiciones; por mapas solo en el 10 % (refinamiento)."""
    eta = eta_mapas(rnd) if rnd.random() < fraccion_mapas else eta_velocidad(rnd)
    return escritura_pg(rnd) + eta


def escalar(servicio, k):
    """Sensibilidad: multiplica todos los tiempos de servicio por k."""
    return lambda rnd: servicio(rnd) * k


def simular(lam, workers, servicio, segundos=120, semilla=7):
    rnd = random.Random(semilla)
    t, llegadas = 0.0, []
    while t < segundos:
        t += rnd.expovariate(lam)
        llegadas.append(t)
    libres = [0.0] * workers
    heapq.heapify(libres)
    respuestas, ocupado = [], 0.0
    for a in llegadas:
        libre = heapq.heappop(libres)
        inicio = max(a, libre)
        s = servicio(rnd)
        fin = inicio + s
        ocupado += s
        heapq.heappush(libres, fin)
        respuestas.append((fin - a) * 1000)  # ms
    respuestas.sort()
    p = lambda q: respuestas[int(q * (len(respuestas) - 1))]
    return {"n": len(respuestas), "p50": p(0.50), "p95": p(0.95), "media": statistics.mean(respuestas),
            "utilizacion": ocupado / (workers * max(max(l for l in libres), segundos))}
