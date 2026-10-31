# Iteración 1 de ADD — Rendimiento (QA-01 y QA-02)

## 1. Entradas revisadas
| Insumo | Origen | Qué aporta |
|--------|--------|------------|
| Restricciones | drivers.md | MVP en 1 mes (R-01), 3 developers con Python/Django (R-02), un solo VPS de bajo costo (R-03) |
| Estilo | ADR-001 | Monolito modular: punto de partida, no se cambia sin evidencia |
| Ingesta y consulta | ADR-002, ADR-003 | HTTPS POST cada 10 s; polling cada 10 s sobre Redis |
| Patrones | ADR-005 | Strategy + Factory para el ETA y Decorators: se agregan tácticas sin reescribir |
| Modelo C4 | workspace.dsl (Lab 06) | Contenedores y componentes actuales |

## 2. Objetivo de la iteración
Cumplir **QA-01** (p95 ≤ 1 s con 14 y 28 req/s) y **QA-02** (p95 ≤ 5 s al procesar 120 pos/s) con 1200 buses.

## 3. Elementos que se refinan
Componentes **Ingesta**, **ETA** y **Seguimiento** de la API, y los contenedores **Caché (Redis)** y **Base de datos (PostgreSQL + PostGIS)**.

## 4. Conceptos de diseño evaluados
| Concepto | Qué mejora | Qué empeora (trade-off) | Decisión |
|----------|------------|-------------------------|----------|
| Migrar a microservicios + Kubernetes + Kafka | Escalabilidad horizontal | Plazo (1 mes), presupuesto (un VPS) y experiencia del equipo | **Rechazado**: la simulación muestra que no hace falta |
| Escalar de 4 a 8 workers (segundo VPS) | Capacidad total | Duplica el costo (R-03) | Plan B. Solo no basta: lectura p95 1269 ms a 28 req/s; ingesta p95 17,8 s |
| Índice espacial (GiST) y consulta acotada por ruta | Tiempo de cada consulta | Escrituras algo más lentas; espacio en disco | **Aceptado**: p95 de 68 ms a 28 req/s |
| Caché del ETA por paradero en Redis con TTL de 10 s | Latencia y carga de la base | ETA de hasta 10 s de antigüedad; más memoria | **Aceptado** como margen; punto de sensibilidad |
| ETA híbrido: por velocidad (EtaPorVelocidad) en el 90 % de las posiciones y por mapas en el 10 % | Costo de cada posición recibida | Precisión del ETA (usa la velocidad actual) | **Aceptado**: p95 de 73 ms a 120 pos/s |

## 5. Decisión
Índice espacial + caché del ETA con TTL de 10 s + ETA híbrido. No se escala todavía. Ver [ADR-006](../adr/006-rendimiento-indice-cache-eta.md).

## 6. Evidencia (simulación M/G/c, 4 workers, 120 s por nivel de carga)
Código: `fitness/rendimiento.py`. Misma medida que el escenario: **p95 en ms**.

**QA-01 — consulta de ETA (p95 en ms)**
| Táctica | 5 req/s | 14 req/s | 28 req/s | ¿Cumple (≤ 1000)? |
|---------|--------:|---------:|---------:|:-----------------:|
| Sin tácticas (hoy) | 546 | 2099 | 111 554 | No |
| Escalar a 8 workers | 521 | 512 | 1269 | No (ráfaga) |
| Índice espacial | 67 | 66 | 68 | Sí |
| Caché con 85 % de aciertos | 310 | 313 | 305 | Sí, con condición |
| **Índice + caché** | **42** | **43** | **41** | **Sí** |

**QA-02 — procesar una posición (p95)**
| Configuración | 30 pos/s (300 buses) | 120 pos/s (1200 buses) | ¿Cumple (≤ 5 s)? |
|---------------|---------------------:|-----------------------:|:----------------:|
| Hoy: escritura + ETA por mapas | 167 ms | 150 035 ms | No |
| Solo escalar a 8 workers | 148 ms | 17 849 ms | No |
| **ETA híbrido (4 workers)** | 68 ms | **73 ms** | **Sí** |

Con 300 buses la versión de hoy cumple (167 ms), de acuerdo con el criterio del ADR-002 (p95 < 300 ms). Con 1200 buses colapsa, y ese es el detonante para revisar el ADR-002.

**Punto de sensibilidad (caché).** Con solo caché, el p95 supera 1 s si los aciertos bajan de **55 %** (por ejemplo, justo después de reiniciar Redis). Con el índice, el p95 sin ninguna caché es 67 ms. Por eso se adoptan ambas: el índice garantiza el escenario y la caché da margen (QA-04).

**Sensibilidad a los supuestos.** Si los tiempos de servicio reales fueran **2 veces** mayores, la ingesta con 4 workers aún cumple (1149 ms); con **2,5 veces** ya no (28 595 ms). El plan B de 8 workers aguanta hasta 3 veces (225 ms).

## 7. ¿Se cumplen los escenarios?
QA-01: **sí** (41 ms frente a 1000 ms). QA-02: **sí** (73 ms frente a 5000 ms).

## Supuestos de la simulación (están escritos en el código)
| Supuesto | Valor | Cómo se valida |
|----------|-------|----------------|
| Hora punta | 60 minutos (14 req/s) y ráfagas de 28 | Confirmar con datos del SIT |
| Workers | 4 (mismo VPS) | Configuración real del servidor |
| Consulta sin índice | mediana 250 ms | Prueba de carga con Locust sobre el prototipo |
| Consulta con índice | mediana 35 ms | Ídem |
| Acierto de caché (Redis) | mediana 4 ms; 85 % de aciertos | Métricas reales de Redis |
| Escritura en PostgreSQL | mediana 8 ms | Prueba de carga |
| ETA por mapas / por velocidad | 60 ms / 1 ms | Medir el proveedor real |
| ETA por mapas solo en 10 % de las posiciones | 10 % | Decisión de diseño |

> **Limitación:** estos tiempos son supuestos, no mediciones. Las conclusiones son tan buenas como los supuestos; por eso se hizo el análisis de sensibilidad y queda como riesgo R3 en el ATAM-lite.
