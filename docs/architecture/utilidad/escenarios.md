# Escenarios del árbol de utilidad — RutaSIT Arequipa (Lab 08)

Escenario de crecimiento (Tabla 11 de la guía): de **300 a 1200 buses** y **50 000 consultas de tiempo de llegada en la hora punta**.
Árbol en Graphviz: [arbol.dot](arbol.dot) · imagen: [arbol.png](arbol.png).

## Supuestos de carga
- Hora punta = 60 minutos: 50 000 consultas ÷ 3600 s = **13,9 req/s** (se usa 14). Ráfagas de **28 req/s** (el doble).
- 1200 buses envían su posición cada 10 s (ADR-002): **120 posiciones por segundo**.
- ADR-003: el pasajero consulta cada 10 s, así que el ETA que ve tiene hasta 10 s más de antigüedad. Por eso, de los 15 s del QA original, quedan **5 s** para procesar la posición.

## Escenarios (seis partes) y calificación (importancia, dificultad)

| ID | Atributo | Fuente | Estímulo | Entorno | Artefacto | Respuesta | Medida | IA | Final |
|----|----------|--------|----------|---------|-----------|-----------|--------|----|-------|
| QA-01 | Rendimiento | Pasajeros (50 000 consultas) | Consultan el ETA de su paradero | Hora punta: 14 req/s, ráfagas de 28 | Consulta de ETA de la API | Devuelve el ETA del paradero | p95 ≤ 1000 ms | (H,H) | **(H,H)** |
| QA-02 | Rendimiento | 1200 buses | Envían su posición cada 10 s (120 pos/s) | Operación normal | Módulo Ingesta | Guarda la posición y recalcula el ETA | p95 del proceso ≤ 5 s | (H,H) | **(H,M)** |
| QA-03 | Disponibilidad | Proveedor de mapas | No responde durante 20 min | Hora punta, 14 req/s | Módulo ETA | Responde con el ETA de respaldo por velocidad | 0 consultas sin ETA y p95 ≤ 1000 ms | (H,H) | **(H,H)** |
| QA-04 | Disponibilidad | Redis | Se reinicia y la caché queda vacía | Ráfaga de 28 req/s | API y PostgreSQL | Responde leyendo de PostgreSQL | p95 ≤ 1000 ms sin la caché | (H,H) | **(H,M)** |
| QA-05 | Seguridad | Usuario del operador A | Lista los viajes | Dos operadores, 600 buses cada uno | Repositorio de viajes | Devuelve solo viajes del operador A | 0 filas del operador B en 200 consultas | (H,M) | **(H,M)** |
| QA-06 | Seguridad | Dispositivo o atacante | Envía una posición con firma inválida o de más de 60 s | Operación normal | Módulo Seguridad | Rechaza el mensaje | 0 aceptados en 1000 alteraciones | (H,M) | **(M,M)** |
| QA-07 | Modificabilidad | Equipo de desarrollo | Incorpora un operador GPS nuevo | Desarrollo | Módulo gps y su Factory | Agrega un adaptador y lo registra | ≤ 1 día-persona; 0 archivos del servicio modificados | (M,L) | **(M,L)** |

## Calificaciones corregidas tras la evidencia

| Escenario | Propuesta inicial | Corrección | Justificación |
|-----------|-------------------|------------|---------------|
| QA-02 | (H,H) | (H,M) | La simulación muestra que con ETA por velocidad la utilización es 0,5 y el p95 es 73 ms: la dificultad real es media. |
| QA-04 | (H,H) | (H,M) | Con el índice espacial, el p95 sin caché es 67 ms: el escenario es difícil de mantener, pero no de lograr. |
| QA-06 | (H,M) | (M,M) | Ya existe HTTPS (ADR-002) y la ingesta no maneja datos personales (R-05): el impacto es menor. |

Prioridad para ADD: (H,H) y (H,M) → **QA-01 y QA-02 → QA-03 y QA-04 → QA-05**.
