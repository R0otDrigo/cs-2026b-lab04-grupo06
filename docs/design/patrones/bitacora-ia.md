# Bitácora de IA (Lab 07)

Registro de las interacciones con IA durante el laboratorio. Las filas **1–6** resumen el
trabajo del equipo en E1–E6 (versión antes, patrones e integración); las filas **7–11**
documentan la sesión real de Riveros para E7–E8. Si alguna fila 1–6 no coincide con la
herramienta o el prompt que usó el equipo, corregirla antes de la entrega.

| # | Fecha | Herramienta | Prompt (resumen) | Propuesta de la IA | Verificación | Decisión |
|---|-------|-------------|------------------|--------------------|--------------|----------|
| 1 | 20/10/2026 | Claude | Detector de olores (Prompt 1) sobre `antes/servicio.py` + salida de radon | 8 olores y patrones | Lectura del código y radon (D 22) | 6 aceptados, 2 rechazados (Singleton, Abstract Factory) |
| 2 | 20/10/2026 | Claude | Refactor solo de GPS y ETA (Strategy + Adapter + Factory) | Cache puesto FUERA del respaldo | Prueba `test_decorator_orden_importa...` en rojo: guardaba el ETA de emergencia | Corregida: cache dentro del respaldo |
| 3 | 21/10/2026 | Claude | Refactor del estado del viaje | Diccionario de transiciones | Válido, pero los estados tendrán comportamiento propio | Rechazada a favor de State |
| 4 | 22/10/2026 | Claude | Guardrails de la explicación del retraso | Usar otro LLM como juez | Costo y latencia extra para un MVP de 1 mes | Rechazada; reglas deterministas |
| 5 | 23/10/2026 | Claude | Diagramas PlantUML desde el código (pyreverse) | Clases y secuencia | Comparación con el código real | Aceptada con correcciones de nombres |
| 6 | 23/10/2026 | Claude | Detectar el error del antes | — | `test_algoritmo_no_soportado_no_consume_el_gps` marcado xfail en antes | Documentado |
| 7 | 23/10/2026 | Freebuff (DeepSeek V4.1 Flash) | Revisar todo el repo y planificar el Turno 3 de Riveros (E7–E8) sin cometer errores | Plan de 4 commits: 8 diagramas, ADR-005, README y CI; detectó que PR2 no existe, que faltan los 8 PNG, que siguen los archivos del Lab 05 y que el token de `gh` no tiene scope `workflow` | `gh` API: PR #12 mergeado y `lab07/e4-e6-sullca` idéntica a `main`; `metricas_equiv.py`: 266 SLOC/6 archivos; conteo: 40 pruebas del Lab 07 + 13 del Lab 05 = 53 | Se acepta el plan: esperar PR2, mantener Lab 05 y ajustar README/CI/métricas; PNG con PlantUML; verificar `clases.puml` con pyreverse |
| 8 | 23/10/2026 | Freebuff (DeepSeek V4.1 Flash) | Ajustar la bitácora de IA con las interacciones reales de esta sesión | Separar el registro del equipo (E1–E6) de la sesión real de E7–E8 y agregar las filas 7–8 | Contraste con las decisiones tomadas y con el estado real del repositorio | Aceptada; las filas 1–6 quedan como registro del equipo y se corrigen si no coinciden con lo que realmente usó |
| 9 | 23/10/2026 | Freebuff (DeepSeek V4.1 Flash) | Ejecutar el Turno 3 y verificar la integración de PR2 | Detectó que `src/rutasit/servicio.py` era el servicio del Lab 05, que `test_patrones.py` fallaba y que el fixture solo corría `rutasit.servicio` | `pytest`: 20 failed, 20 passed antes; `radon`: `consultar_eta` 5 (A) | Corregido: se restauró `servicio.py` con patrones, `servicios.py` legado y el fixture de dos versiones; resultado 53 passed + 1 xfailed |
| 10 | 23/10/2026 | Freebuff (DeepSeek V4.1 Flash) | Generar los 8 PNG y verificar `clases.puml` con pyreverse | Diagramas PlantUML y ajuste del diagrama de clases: paquete del dominio Lab 05 como legado, atributos de `Viaje` y relación `ServicioEta → Viaje` | `plantuml -checkonly` sin errores; 8 PNG generados; pyreverse: 14 módulos y 12 imports | Aceptado: diagramas y `clases.puml` consistentes con el código; el dominio del Lab 05 queda marcado como legado |
| 11 | 23/10/2026 | Freebuff (DeepSeek V4.1 Flash) | Ajustar README y métricas a la suite real | README con 40 passed + 1 xfailed del Lab 07 y 53 passed + 1 xfailed de la suite completa; métricas 3 (A), 1,64 (A), 266 SLOC y 6 archivos | `pytest` y `radon` reales sobre la rama | Aceptado: las cifras del README y `metricas.md` coinciden con la ejecución |

**Total:** 11 interacciones registradas; 2 correcciones por pruebas (filas 2 y 9). No se incluyó
información personal, credenciales ni claves de API en ningún prompt; el token de `gh` se
usó solo para consultar el estado del repositorio y no se transcribió.
