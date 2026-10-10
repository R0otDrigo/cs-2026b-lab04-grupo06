# Revisión de consistencia (C1–C5) — RutaSIT Arequipa

Se corrió `verificar_consistencia.py` (script escrito con ayuda de IA) sobre `clases.puml`,
`secuencia-consultar-eta.puml`, `estados-viaje.mmd` y `paquetes.puml`. C3 se revisó a mano.

| Regla | Hallazgo | Verificación del equipo |
|-------|----------|-------------------------|
| C1 | 6 mensajes de la secuencia hacia objetos del dominio. Ninguno sin operación. | Correcto: `consultarEta`, `buscarActivosPorParadero`, `ultimaPosicion`, `estaSinSenal`, `tiempoDeRecorrido` y `avisarSinSenal` existen en el diagrama de clases. |
| C2 | 9 transiciones del diagrama de estados. Ninguna sin operación. | Correcto: todas usan operaciones de `Viaje`. Cada una tiene su prueba en `tests/test_viaje.py`. |
| C3 | Revisión manual de multiplicidades. | Correcto: Ruta 1..* — 2..* Paradero (una ruta tiene al menos 2 paraderos), Viaje 1 *-- 0..* Posicion, Bus 1 — 0..* Viaje. |
| C4 | Sin ciclos entre los paquetes. | Correcto: `seguimiento` no depende de `alertas`; `ingesta` coordina a los dos (ver ADR-004). |
| C5 | 10 hallazgos: "el nombre `estaSinSenal` no coincide con el código". | **Falso positivo.** En el código es `esta_sin_senal` por convención de Python. La equivalencia está documentada en `round-trip.md`. |

## Qué habría pasado si aceptábamos el falso positivo

Habríamos renombrado 10 métodos del código a camelCase. Eso rompe la convención de Python (PEP 8)
y habría dejado el código distinto al resto del proyecto, sin ninguna ganancia.
