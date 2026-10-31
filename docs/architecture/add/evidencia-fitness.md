# Evidencia de las fitness functions — RutaSIT (Lab 08)

## Ejecución correcta (rama sin violaciones)
```
$ PYTHONPATH=src lint-imports
Contracts
---------

Analyzed 15 files, 13 dependencies.
-----------------------------------

FF-01 Capas del nucleo: servicios y adaptadores -> puertos -> dominio (ADR-001) KEPT
FF-02 Los patrones no se conocen entre si; solo el servicio los compone 
(ADR-005) KEPT
FF-03 Estrategias, adaptadores y dominio no importan los SDK externos (ADR-005) KEPT
FF-04 El codigo vigente no depende de la version antes (ADR-005) KEPT

Contracts: 4 kept, 0 broken.
```
`PYTHONPATH=src pytest -q` → **71 passed, 1 xfailed** (el xfail es el defecto documentado de la versión antes del Lab 07).

## Violación 1 (estructural): atajos "temporales"
Se agregó `from rutasit.externos import MapasOSM` en `eta.py` y `from rutasit.servicios import ServicioEta` en `dominio.py`.
```
Broken contracts
----------------

FF-01 Capas del nucleo: servicios y adaptadores -> puertos -> dominio (ADR-001)
-------------------------------------------------------------------------------

rutasit.dominio is not allowed to import rutasit.servicios:

- rutasit.dominio -> rutasit.servicios (l.2)


FF-03 Estrategias, adaptadores y dominio no importan los SDK externos (ADR-005)
-------------------------------------------------------------------------------

rutasit.eta is not allowed to import rutasit.externos:

-   rutasit.eta -> rutasit.externos (l.2)


rutasit.resiliencia is not allowed to import rutasit.externos:

-   rutasit.resiliencia -> rutasit.eta (l.6)
    rutasit.eta -> rutasit.externos (l.2)



```

Las violaciones se revirtieron (se hicieron sobre una copia del repositorio) y los 4 contratos vuelven a quedar en KEPT.

## Violación 2 (calidad): alguien quita el índice espacial
Se cambió la mediana de la consulta con índice de 35 ms a 250 ms (la consulta vuelve a ser lenta). Resultado de `pytest test/test_fitness.py`:
```
E       AssertionError: p95=110849 ms con la cache vacia
test/test_fitness.py:28: AssertionError
FAILED test/test_fitness.py::test_ff06_qa04_cache_fria_sigue_cumpliendo_con_el_indice
1 failed, 9 passed in 0.30s
```
**Hallazgo:** FF-05 (con caché del 85 %) seguía en verde porque la caché tapaba la ausencia del índice; solo **FF-06** (caché fría) detectó la degradación. Por eso se necesitan las dos pruebas.

## Violación 3 (disponibilidad): alguien quita el circuit breaker
Sin el breaker (variante "Reintentos + respaldo") el p95 durante la caída es **6005 ms** y las llamadas al proveedor son **50 811**: FF-08 (p95 ≤ 1000 ms) y FF-09 (llamadas < 1/50) fallan.

## Cómo reproducirlo
```
pip install import-linter pytest
PYTHONPATH=src lint-imports
PYTHONPATH=src pytest -v test/test_fitness.py test/test_circuit_breaker.py
```
