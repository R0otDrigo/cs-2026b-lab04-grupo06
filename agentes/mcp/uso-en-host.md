# Uso del servidor en un host real (E5)

Host: VS Code con GitHub Copilot en modo agente (configuración en `.vscode/mcp.json`). Alternativa: Claude Code con `.mcp.json` en la raíz.

> Estado de esta entrega: se incluyen las configuraciones y el protocolo de prueba.
> La conexión a VS Code/Copilot y las cinco consultas todavía deben verificarse
> en el host; las columnas vacías no representan resultados obtenidos.

```json
{ "servers": { "rutasit": { "type": "stdio", "command": "python",
  "args": ["${workspaceFolder}/agentes/mcp/servidor_mcp/rutasit_mcp.py"] } } }
```

Pasos: seleccionar un entorno Python con las dependencias de `requirements.txt` instaladas, abrir el repositorio en VS Code, abrir `.vscode/mcp.json` y pulsar **Start** sobre `rutasit`; en el chat de Copilot elegir el modo **Agent** y comprobar en el ícono de herramientas que aparecen `buses_en_ruta`, `tiempo_llegada`, `estado_desvio` y `reportar_desvio`. El comando `python` de ambas configuraciones debe resolver a ese entorno. El servidor no usa claves de API ni variables secretas.

## Las 5 consultas

La columna "Resultado esperado" se obtuvo llamando al servidor directamente (son los datos ficticios de `flota_demo.py`), así que sirve para juzgar si el host respondió bien. Las columnas del host se llenan al hacer la prueba.

| # | Consulta en lenguaje natural | Herramienta o primitiva esperada | Resultado esperado (servidor) | Herramienta que eligió el host | ¿Pidió permiso? | ¿Correcto? |
|---|---|---|---|---|---|---|
| 1 | ¿En cuántos minutos llega el próximo bus de la ruta 7 a Plaza de Armas? | `tiempo_llegada(R-07, Plaza de Armas)` | V1A-456 en 3 min (V2B-789 está desviado y no cuenta) | | No debería | |
| 2 | ¿Qué buses de la ruta 12 están en servicio? ¿Alguno está desviado? | `buses_en_ruta(R-12)` | V1A-321 (km 0,8) y V2B-654 (km 1,7); ninguno desviado | | No debería | |
| 3 | Estoy en Puente Grau, ruta 7. ¿Cuánto falta? | `tiempo_llegada(R-07, Puente Grau)` | V1A-123 en 2 min (V1A-456 ya pasó el paradero) | | No debería | |
| 4 | Prompt del servidor: `/mcp.rutasit.aviso_usuarios` con ruta `R-07` y situación "bus V2B-789 desviado por la curva" | prompt `aviso_usuarios` | Aviso de 280 caracteres como máximo, sin inventar horarios | | No aplica | |
| 5 | Reporta el desvío del bus V2B-789 con la evidencia. | `reportar_desvio(V2B-789, ...)` (tras `buses_en_ruta`) | Crea `agentes/mcp/reportes/DESVIO-01.md` | | **Sí, obligatorio** | |

Comprobación de la escritura: después de la consulta 5 debe existir `agentes/mcp/reportes/DESVIO-01.md`. Si se pide reportar `V1A-123`, el servidor responde con `isError: true` porque ese bus no cumple RF-04, y el host debería explicarlo en lugar de insistir.

## Observaciones

_(Completar después de la prueba: si el host eligió una herramienta distinta, si pidió permiso para alguna de lectura, si hubo que reformular alguna consulta y cuánto tardó en arrancar el servidor.)_
