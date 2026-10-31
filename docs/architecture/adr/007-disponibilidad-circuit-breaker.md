# ADR-007: Circuit breaker y ETA de respaldo ante la caída del proveedor de mapas

- Estado: Aceptado
- Fecha: 2026-10-29
- Decisores: Estefanero Palma Rodrigo, Sullca Mamani Mauro Snayder y Riveros Vilca Alberth Edwar

## Contexto
QA-03 exige que, si el proveedor de mapas cae 20 minutos, no haya consultas sin ETA y el p95 siga ≤ 1 s. El Lab 07 ya implementó reintentos (ConReintentosEta) y un ETA de respaldo por velocidad (ConRespaldo). La simulación muestra que eso solo **no alcanza**: cada consulta espera los tres timeouts y el p95 es de 6005 ms, con 50 811 llamadas al proveedor caído (riesgo R6).

## Alternativas consideradas
1. Dejar solo reintentos + respaldo. Rechazada: p95 de 6005 ms.
2. Agregar una cola de pendientes. Rechazada: el ETA es una lectura sin efectos; no se puede "diferir".
3. Un segundo proveedor de mapas. Plan B: costo y complejidad (R-03).
4. Agregar un circuit breaker como Decorator. Aceptada.

## Decisión
Usaremos `ConCircuitBreakerEta` (umbral de 3 fallas, espera de 30 s) como Decorator entre la caché y los reintentos. `CircuitoAbierto` hereda de `TimeoutError` para que `ConRespaldo` lo atienda sin modificar el código del Lab 07. La composición en `servicio.py` pasa a ser: `ConRespaldo(ConCacheEta(ConCircuitBreakerEta(ConReintentosEta(EtaPorMapas))), EtaPorVelocidad)`.

## Consecuencias
- Positivas: con el proveedor caído, 0 consultas sin ETA, p95 de 5 ms y 126 llamadas en lugar de 50 811 (99,8 % menos).
- Negativas / riesgos: durante la caída el ETA es menos preciso (solo velocidad); el umbral y la espera hay que calibrarlos (R5); se agrega una clase más y 8 pruebas.
- Evidencia: add/iteracion-2.md, src/rutasit/resiliencia.py, test/test_circuit_breaker.py, FF-08 y FF-09.
