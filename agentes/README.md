# Sistema agéntico de RutaSIT (Laboratorio 10)

Basado en el mini framework del curso (`README-framework-original.md`), adaptado a RutaSIT. Todo se ejecuta desde esta carpeta.

```text
pip install -r ../requirements.txt
python -m pytest -q pruebas_agente                       # contrato, política, sandbox, herramientas, humano y corridas grabadas
python orquestador.py --issue 1 --modo unico             # reproduce la trayectoria grabada (sin clave de API)
python orquestador.py --issue 1 --modo unico --interactivo        # graba una nueva con su asistente de IA
python orquestador.py --issue 2 --modo coordinado --humano consola
python agente/traza.py trazas/issue1_unico --png          # .mmd + metricas.json (+ .png si hay mermaid-cli)
python diagramas/metricas.py                              # gráficos de E4, E5 y E7
```

| Carpeta o archivo | Contenido |
|---|---|
| `agente/` | Núcleo ReAct, contrato, política, herramientas (+ `mapa_repo`, notas), modelos, humano en el circuito, trazas |
| `trabajo_original/` | Copia del código con los 3 errores, sus pruebas y los issues. Cada corrida la copia a `trabajo/` (ignorada por git) |
| `trayectorias/<corrida>/` | Decisiones grabadas de cada agente y `humano.json` |
| `trazas/<corrida>/` | JSONL por agente, `cambios.diff`, `resumen.json`, `metricas.json`, `trayectoria.mmd/.png` |
| `diseno/` | Lienzo (E1), máquina de estados (E3), arquitectura y delegación |
| `observacion.md`, `delegacion.md`, `bitacora-ia.md`, `cuestionario.md` | E4 a E7 y cuestionario |

Cambios al framework original: `test/` protegida además de `tests/`; `aprobar_edicion` como campo de la política; protocolo JSON en el objetivo; el texto no JSON pasa al contrato en vez de cerrar el programa; `sys.executable` para pytest; trazas con inicio y final de cada observación; orquestador con modos `unico`/`coordinado`, herramientas básicas/extendidas y humano `consola`/`grabado`.
