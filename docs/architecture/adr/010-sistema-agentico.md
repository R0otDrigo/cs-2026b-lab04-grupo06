# ADR-010: Arquitectura del sistema agéntico para resolver issues de RutaSIT

- Estado: Aceptado
- Fecha: 2026-11-21
- Decisores: Estefanero Palma Rodrigo, Sullca Mamani Mauro Snayder y Riveros Vilca Alberth Edwar

## Contexto
El Lab 10 pide un sistema agéntico que resuelva issues del propio repositorio. Para RutaSIT se sembraron 3 issues con prueba en rojo: el GPS del operador A sin datos tumba el servicio (#1), el ETA sale negativo si el bus ya pasó el paradero (#2) y no se detecta el desvío en curvas (#3). El agente ejecuta herramientas reales (pytest, radon, edición de archivos), así que un error suyo puede romper código o ejecutar algo peligroso (OWASP LLM06, exceso de agencia).

## Alternativas consideradas
1. Flujo fijo (leer issue, correr pruebas, pedir parche, aplicar). Rechazada para los issues: no se sabe de antemano qué archivo tocar. Se mantiene para tareas repetitivas (diagramas C4, evals de prompts).
2. Agente único ReAct con todas las herramientas y sin aprobación. Rechazada: en el issue 2 el agente único pasó la prueba y dejó un `TypeError` en `consultar_eta()`.
3. Coordinación democrática con tres revisores. Rechazada por ahora: triplica el costo del crítico sin evidencia de que un solo revisor no alcance.
4. Agente único por defecto y planificador + ejecutor + revisor (actor-crítico, máx. 2 rondas) cuando el cambio altera un contrato público, con aprobación humana de cada edición. Aceptada.

## Decisión
- Arquetipo: ReAct dentro de una máquina de estados (`agentes/agente/nucleo.py`), con un planificador previo en el modo coordinado.
- Coordinación: por gestor (`orquestador.py`) y actor-crítico; el revisor es de solo lectura.
- Herramientas: 7 básicas con alcance mínimo; `ejecutar_comando` solo acepta `python -m pytest`, `radon cc`, `lint-imports` y `git status/diff`. `mapa_repo`, `anotar` y `leer_notas` se activan con `--herramientas extendidas`.
- Memoria: historial de la tarea; pizarra `notas.md` en el sandbox para pasar información entre rondas.
- Límites: contrato JSON validado antes de actuar; 12 pasos el ejecutor, 8 el revisor, 2 el planificador; `test/` y `tests/` protegidas; sandbox `agentes/trabajo/` copiado de `trabajo_original/` en cada corrida; nunca en `main` ni con credenciales.
- Rol humano: revisor. Aprueba cada edición con `s`/`n` (`--humano consola`) y aprueba el Pull Request; ningún agente fusiona su propio cambio.

## Consecuencias
- Positivas: los 3 issues se resolvieron sin modificar pruebas; el revisor encontró un error que la prueba del issue no cubría; cada corrida deja traza JSONL, diff y diagrama Mermaid, y se reproduce sin clave de API (37 pruebas en `agentes/pruebas_agente/`).
- Negativas / riesgos: el actor-crítico costó 2,9 veces más pasos y 4,5 veces más contexto en el issue 2; la aprobación por edición frena el trabajo; las trayectorias las produjo un solo modelo, así que otra grabación puede tomar otro camino; `mapa_repo` no ahorró contexto en un repositorio de 15 módulos.
- Evidencia: `agentes/observacion.md`, `agentes/delegacion.md`, `agentes/bitacora-ia.md`, `agentes/trazas/`, `agentes/diseno/estados.puml`.
