# Iteración 2 de ADD — Disponibilidad (QA-03 y QA-04)

## 1–3. Entradas, objetivo y elemento
Entradas: las de la iteración 1 más ADR-006. Objetivo: **QA-03** (el proveedor de mapas cae 20 minutos: 0 consultas sin ETA y p95 ≤ 1 s) y **QA-04** (caché fría). Elemento que se refina: el componente **ETA** y su cadena de decoradores (Lab 07). Riesgo que mitiga: **R6** (dependencia del proveedor de mapas).

## 4. Conceptos de diseño evaluados
| Concepto | Qué mejora | Qué empeora (trade-off) | Decisión |
|----------|------------|-------------------------|----------|
| Solo reintentos (3) | Tolera fallas cortas | Sobrecarga al proveedor caído | Insuficiente: 16 937 consultas sin ETA |
| Reintentos + ETA de respaldo por velocidad (ya existe, Lab 07) | Siempre hay ETA | Cada consulta espera los 3 timeouts | Insuficiente: **p95 de 6005 ms** (> 1000 ms) y 50 811 llamadas |
| **Reintentos + respaldo + circuit breaker** (Decorator nuevo) | Respuesta rápida y protege al proveedor | ETA menos preciso mientras dura la caída; hay que calibrar umbral y espera (R5) | **Aceptado** |
| Cola de pendientes (como en un pago) | No se pierden operaciones | No aplica: el ETA es una lectura sin efectos; no tiene sentido diferirla | **Rechazado** |
| Segundo proveedor de mapas | Redundancia total | Costo y complejidad (R-03) | Plan B |

## 5. Decisión
Agregar `ConCircuitBreakerEta` (umbral 3 fallas, espera 30 s) como Decorator entre la caché y los reintentos. Se compone sin modificar los decoradores existentes: `CircuitoAbierto` es un `TimeoutError`, así que `ConRespaldo` lo atiende como una caída normal. Ver [ADR-007](../adr/007-disponibilidad-circuit-breaker.md). Código: `src/rutasit/resiliencia.py` y `test/test_circuit_breaker.py` (8 pruebas, una por transición).

## 6–7. Evidencia (Monte Carlo con las clases reales del repositorio)
Código: `fitness/disponibilidad.py`. 40 minutos de simulación a 14 consultas/s; el proveedor cae entre el minuto 10 y el 30.

| Variante | Consultas sin ETA | p95 durante la caída | Llamadas al proveedor caído |
|----------|------------------:|---------------------:|----------------------------:|
| Sin tácticas | 16 937 | 2000 ms | 16 937 |
| Reintentos (3) | 16 937 | 6000 ms | 50 811 |
| Reintentos + respaldo | 0 | 6005 ms | 50 811 |
| **Reintentos + respaldo + breaker** | **0** | **5 ms** | **126** |

El breaker reduce de 50 811 a **126** las llamadas al proveedor caído (**99,8 %** menos) y el p95 de 6005 ms a 5 ms. **QA-03 se cumple.**

**QA-04.** Con la caché vacía (0 % de aciertos) y el índice espacial, el p95 a 28 req/s es **67 ms** (FF-06). **Se cumple.**

## Supuestos
Timeout del cliente 2 s; respuesta normal del proveedor 50 ms; ETA por velocidad 5 ms; 14 consultas/s; caída de 20 min. El ETA de respaldo es **menos preciso** que el de mapas: durante la caída el pasajero ve un ETA calculado solo con la velocidad del bus.
