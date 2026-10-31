# ADR-006: Índice espacial, caché del ETA y ETA híbrido para el crecimiento a 1200 buses

- Estado: Aceptado
- Fecha: 2026-10-29
- Decisores: Estefanero Palma Rodrigo, Sullca Mamani Mauro Snayder y Riveros Vilca Alberth Edwar

## Contexto
El escenario de crecimiento lleva a RutaSIT de 300 a 1200 buses y a 50 000 consultas de ETA en la hora punta (QA-01: p95 ≤ 1 s a 14 req/s y 28 req/s de ráfaga; QA-02: procesar 120 posiciones por segundo con p95 ≤ 5 s). Restricciones: 1 mes (R-01), 3 developers de Python/Django (R-02) y un solo VPS (R-03). El ADR-002 pedía revisar la ingesta si la carga superaba lo previsto, y el ADR-005 dejó la base de patrones (Strategy + Factory, Decorator) para agregar tácticas sin reescribir.

## Alternativas consideradas
1. Microservicios + Kubernetes + Kafka. Rechazada: no cabe en el plazo ni en el presupuesto y la simulación muestra que no hace falta.
2. Escalar de 4 a 8 workers (segundo VPS). Plan B: duplica el costo y por sí sola no cumple (lectura 1269 ms a 28 req/s; ingesta 17 849 ms).
3. Índice espacial (GiST) y consulta acotada por ruta. Aceptada.
4. Caché del ETA por paradero en Redis con TTL de 10 s. Aceptada como margen.
5. ETA híbrido: EtaPorVelocidad en el 90 % de las posiciones y EtaPorMapas en el 10 %. Aceptada.

## Decisión
Usaremos un **índice espacial GiST** en la tabla de posiciones y consultas acotadas por ruta; una **caché de ETA por paradero en Redis con TTL de 10 s** (alineada con el polling de 10 s del ADR-003); y un **ETA híbrido** en la ingesta, elegido mediante la Factory de estrategias del Lab 07. No escalaremos todavía; el plan B es pasar a 8 workers si una prueba de carga real muestra tiempos de servicio 2,5 veces mayores que los supuestos.

## Consecuencias
- Positivas: p95 de lectura de 41 ms a 28 req/s (simulación) y de ingesta de 73 ms a 120 pos/s; costo casi nulo; sin cambiar el estilo del ADR-001.
- Negativas / riesgos: el ETA puede tener hasta 10 s de antigüedad (R4); el ETA por velocidad es menos preciso que el de mapas (trade-off aceptado); los tiempos de servicio de la simulación son supuestos (R3): hay que validarlos con una prueba de carga real.
- Evidencia: add/iteracion-1.md, fitness/rendimiento.py, FF-05, FF-06 y FF-07.
