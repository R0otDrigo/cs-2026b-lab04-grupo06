"""FITNESS FUNCTIONS de calidad (Lab 08): cada escenario del arbol de utilidad convertido en una prueba.
Las FF-01 a FF-04 (estructura) las ejecuta import-linter con el archivo .importlinter."""
import pathlib
import random
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from fitness import auth_gps  # noqa: E402
from fitness.aislamiento import base_de_prueba  # noqa: E402
from fitness.disponibilidad import simular as simular_eta_caida  # noqa: E402
from fitness.rendimiento import (bd_con_indice, con_cache, ingesta_eta_hibrido, simular)  # noqa: E402

PRESUPUESTO_LECTURA_P95_MS = 1000     # QA-01: p95 <= 1 s
PRESUPUESTO_INGESTA_P95_MS = 5000     # QA-02: ETA <= 15 s en total = 10 s de polling + 5 s de proceso


def test_ff05_qa01_consulta_de_eta_en_hora_punta_y_rafaga():
    for lam in (14, 28):
        r = simular(lam=lam, workers=4, servicio=con_cache(bd_con_indice))
        assert r["p95"] <= PRESUPUESTO_LECTURA_P95_MS, f"p95={r['p95']:.0f} ms a {lam} req/s"


def test_ff06_qa04_cache_fria_sigue_cumpliendo_con_el_indice():
    r = simular(lam=28, workers=4, servicio=con_cache(bd_con_indice, tasa_aciertos=0.0))
    assert r["p95"] <= PRESUPUESTO_LECTURA_P95_MS, f"p95={r['p95']:.0f} ms con la cache vacia"


def test_ff07_qa02_ingesta_de_1200_buses():
    r = simular(lam=120, workers=4, servicio=ingesta_eta_hibrido)
    assert r["p95"] <= PRESUPUESTO_INGESTA_P95_MS, f"p95={r['p95']:.0f} ms a 120 pos/s"


def test_ff08_qa03_cero_consultas_sin_eta_y_latencia_baja_con_el_proveedor_caido():
    r = simular_eta_caida("Reintentos + respaldo + breaker")
    assert r["sin_eta"] == 0
    assert r["p95_ms"] <= PRESUPUESTO_LECTURA_P95_MS, f"p95={r['p95_ms']:.0f} ms durante la caida"


def test_ff09_el_breaker_protege_al_proveedor_caido():
    con = simular_eta_caida("Reintentos + respaldo + breaker")["llamadas_en_caida"]
    sin = simular_eta_caida("Reintentos + respaldo")["llamadas_en_caida"]
    assert con < sin / 50


def test_ff10_qa05_un_operador_nunca_ve_buses_de_otro():
    repo = base_de_prueba(600)
    for i in range(200):
        propio, ajeno = ("OPERADOR_A", "B-") if i % 2 == 0 else ("OPERADOR_B", "A-")
        filas = repo.listar(propio)
        assert len(filas) == 600
        assert all(op == propio and not placa.startswith(ajeno) for placa, op in filas)


def test_ff10_el_repositorio_no_permite_consultar_sin_operador():
    with pytest.raises(ValueError):
        base_de_prueba(5).listar("")


SECRETO = b"secreto-del-operador-a"


def test_ff11_qa06_mensaje_valido_se_acepta():
    f = auth_gps.firmar(SECRETO, "A-0001", -16.4, -71.53, 1000)
    assert auth_gps.verificar(SECRETO, "A-0001", -16.4, -71.53, 1000, f, ahora=1010)


def test_ff11_qa06_ninguna_alteracion_de_1000_se_acepta():
    rnd = random.Random(3)
    f = auth_gps.firmar(SECRETO, "A-0001", -16.4, -71.53, 1000)
    aceptados = 0
    for _ in range(1000):
        bus = rnd.choice(["A-0001", "A-0002", "B-0001"])
        lat, lon = -16.4 + rnd.uniform(-1, 1) * 0.01, -71.53 + rnd.uniform(-1, 1) * 0.01
        if (bus, lat, lon) == ("A-0001", -16.4, -71.53):
            continue
        aceptados += auth_gps.verificar(SECRETO, bus, lat, lon, 1000, f, ahora=1010)
    assert aceptados == 0


def test_ff11_qa06_mensaje_viejo_o_de_otro_operador_se_rechaza():
    f = auth_gps.firmar(SECRETO, "A-0001", -16.4, -71.53, 1000)
    assert not auth_gps.verificar(SECRETO, "A-0001", -16.4, -71.53, 1000, f, ahora=1000 + 120)
    assert not auth_gps.verificar(b"secreto-del-operador-b", "A-0001", -16.4, -71.53, 1000, f, ahora=1010)
