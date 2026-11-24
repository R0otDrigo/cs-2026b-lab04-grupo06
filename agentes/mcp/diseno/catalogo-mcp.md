# Catálogo del servidor MCP `rutasit` (E1)

Grupo 06 · RutaSIT Arequipa · Laboratorio 11

El servidor publica una sola vez lo que hoy está dentro del backend y del agente del Lab 10, para que lo usen el agente, VS Code con Copilot o Claude Code sin reescribir nada. Partimos de la Tabla 14 de la guía (caso 6) y del código real: el ETA sale de `rutasit.llegada` (HU-01, issue #2) y el desvío de `rutasit.desvio` (RF-04, issue #3). Los datos de la flota son ficticios.

| Capacidad | Primitiva | ¿Escribe? | Justificación |
|---|---|---|---|
| Buses en servicio de una ruta | Herramienta `buses_en_ruta` | No | Consulta con un parámetro que el modelo elige (la ruta) |
| Minutos hasta un paradero | Herramienta `tiempo_llegada` | No | Cálculo con parámetros; reutiliza `minutos_hasta_paradero` y la regla "ETA no disponible" |
| Desvíos según RF-04 | ~~Herramienta `estado_desvio`~~ fusionada en `buses_en_ruta` (E6) | No | Cada bus trae `distancia_ruta_m` y `desviado`; reutiliza `distancia_a_ruta` y `hay_desvio` |
| Reportar un desvío | Herramienta `reportar_desvio` ★ | Sí, solo crea | Única escritura: crea `reportes/DESVIO-NN.md`; nunca edita ni borra |
| Mapa de rutas (paraderos por km y trazado) | Recurso `rutasit://rutas` (JSON) | No | Contexto estable; lo decide el host |
| Reglas aprobadas HU-01, RF-01, RF-04 | Recurso `rutasit://reglas` | No | Contexto estable para no repetir las reglas en cada prompt |
| ADR por número | Recurso plantilla `rutasit://adr/{numero}` | No | Decisiones de arquitectura; acepta solo 3 dígitos |
| Aviso a usuarios | Prompt `aviso_usuarios` | No | Plantilla que el usuario invoca ante un desvío o retraso |
| Criterios de aceptación | Prompt `criterios_aceptacion` | No | Prompt v5 del Lab 09, leído de `prompts/criterios/v5.txt` |

## Descripciones escritas antes de programar

- `buses_en_ruta(ruta)`: lista los buses en servicio de una ruta con operador (A o B), km recorridos desde el inicio, velocidad (km/h) y última posición. `ruta`: código con guion, R-07 o R-12. Devuelve una lista; ruta desconocida: error con los códigos válidos.
- `tiempo_llegada(ruta, paradero)`: minutos hasta que el próximo bus llegue al paradero, medidos sobre la ruta. Omite buses que ya pasaron el paradero y buses desviados. `paradero`: nombre exacto de un paradero de esa ruta. Devuelve `{ruta, paradero, disponible, minutos, placa, mensaje}`; si ningún bus puede llegar, `disponible=false` y "ETA no disponible".
- `estado_desvio(ruta)`: para cada bus, la distancia de su última posición al trazado (m) y si está desviado (más de 150 m en dos posiciones seguidas).
- `reportar_desvio(placa, descripcion)`: crea un reporte nuevo. `placa`: formato V1A-123. `descripcion`: 20 a 800 caracteres con lo observado y la evidencia. Rechaza buses que no cumplen RF-04.

## Por qué la escritura no puede causar daño irreversible

`reportar_desvio` abre el archivo en modo `"x"`, que falla si el archivo ya existe, así que no puede sobrescribir. Calcula el número siguiente al mayor existente y no borra nada. Solo acepta buses que el propio servidor confirma como desviados con RF-04, así que no se puede usar para llenar la carpeta de reportes falsos. Su descripción tiene un máximo de 800 caracteres y va anotada con `readOnlyHint=false`, `destructiveHint=false` e `idempotentHint=false` para que el host pida permiso. Lo peor que puede pasar es un reporte de más, y se borra a mano.

## Lo que no se expone

No hay herramientas para cambiar el estado de un viaje, editar rutas o enviar notificaciones a pasajeros. Esas acciones afectan a usuarios reales y quedan fuera del servidor, aunque existan en el dominio (`estados.py`, `NotificadorPasajero`).

## Cambio en E6: catálogo optimizado

La traza de E4 mostró que el agente siempre llamaba a `buses_en_ruta` y luego a `estado_desvio` sobre la misma ruta. En E6 fusionamos las dos: `buses_en_ruta` devuelve ahora `distancia_ruta_m` y `desviado` por bus (y ya no la latitud y longitud, que el agente no usaba), y acortamos las descripciones. El catálogo pasó de 4 a 3 herramientas y de ~1151 a ~805 tokens (−30 %). Detalle en `../protocolo.md`.
