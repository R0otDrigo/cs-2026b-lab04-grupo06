# Lienzo de diseño del sistema agéntico (E1)

Grupo 06 · RutaSIT Arequipa · Laboratorio 10

Tarea del sistema: resolver issues pequeños del backend de RutaSIT (`src/rutasit`) que ya tienen una prueba que los reproduce. "Resuelto" significa que la prueba del issue pasa, que las 61 pruebas anteriores que se copiaron al sandbox siguen en verde y que ninguna prueba fue modificada.

| Decisión de diseño | Elección para RutaSIT | Justificación |
|---|---|---|
| ¿Agente o flujo de trabajo? | Agente para los issues 1, 2 y 3. Flujo fijo para regenerar diagramas C4 y correr las evaluaciones de prompts (Labs 06 y 09). | En un issue no sabemos de antemano qué archivo tocar: hay que leer el issue, reproducirlo y explorar (Sección 1.1). Regenerar diagramas o correr `promptfoo` son siempre los mismos pasos, así que un workflow de GitHub Actions es más barato y predecible. |
| Arquetipo | ReAct para el agente único; planificador-ejecutor con ReAct dentro del ejecutor en el modo coordinado. | ReAct sirve para explorar el repositorio hasta encontrar la causa (Tabla 3). El plan previo es corto y legible, y la persona que revisa sabe qué esperaba el sistema antes de ver el diff. |
| Herramientas | Las 7 básicas (listar, leer, buscar, ejecutar pruebas, editar, ver cambios, comandos permitidos) y, en E4, `mapa_repo`, `anotar` y `leer_notas`. | Es lo mínimo para leer, cambiar y verificar (Tabla 5). `ejecutar_comando` solo acepta `python -m pytest`, `radon cc`, `lint-imports` y `git status/diff`. |
| Memoria | Corto plazo (historial de la tarea). En E4, una pizarra `notas.md` dentro del sandbox. | Los issues se resuelven en menos de 12 pasos. La pizarra sirve para que el ejecutor de la ronda 2, que empieza con historial nuevo, sepa qué se revisó en la ronda 1. |
| Coordinación | Por gestor (planificador) + actor-crítico (ejecutor y revisor de solo lectura), máximo 2 rondas. También se mide el agente único para comparar (E5). | Separa quién cambia el código de quién lo revisa. Por parsimonia (Albada, cap. 8) el modo coordinado se usa solo si el issue cambia un contrato público, como el issue 2. |
| Rol humano | Revisor: aprueba cada edición desde la consola (`s`/`n`) y aprueba el Pull Request. | Es el primer uso del sistema y la confianza es baja (Sección 1.8). Ningún agente fusiona su propio cambio. |
| Control | Contrato JSON validado antes de actuar; política por rol; `test/` y `tests/` protegidas; 12 pasos el ejecutor, 8 el revisor, 2 el planificador; sandbox `agentes/trabajo/`. | Evita acciones indebidas, bucles y que el agente "arregle" las pruebas para que pasen. |

## Issues de la tarea

| Issue | Prueba que lo reproduce | Estado antes del agente |
|---|---|---|
| [#1 GPS del operador A sin datos](../../issues/ISSUE-01.md) | `tests/test_issue_01_gps_sin_datos.py` | 4 fallan (`TypeError`, `KeyError`) |
| [#2 ETA negativo si el bus ya pasó](../../issues/ISSUE-02.md) | `tests/test_issue_02_eta_paradero_pasado.py` | 1 de 3 falla (devuelve -2) |
| [#3 Desvío no detectado en curvas](../../issues/ISSUE-03.md) | `tests/test_issue_03_desvio_curvas.py` | 2 de 3 fallan |

El issue 1 es un error real del código del Lab 07. Los issues 2 y 3 describen funciones que no existían (`llegada.py` y `desvio.py`); se implementaron con el error incluido, como permite la guía, siguiendo HU-01 y RF-04 del diseño aprobado.
