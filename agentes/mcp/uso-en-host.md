# Uso del servidor en un host real (E5)

Host: VS Code con GitHub Copilot en modo agente (configuración en `.vscode/mcp.json`). Alternativa: Claude Code con `.mcp.json` en la raíz.

```json
{ "servers": { "rutasit": { "type": "stdio", "command": "python",
  "args": ["${workspaceFolder}/agentes/mcp/servidor_mcp/rutasit_mcp.py"] } } }
```

Pasos: abrir el repositorio en VS Code, abrir `.vscode/mcp.json` y pulsar **Start** sobre `rutasit`. En el chat de Copilot, elegir **Agent** y abrir **Configure Tools**. Para la prueba de E5 se usó Python 3.12 y el ejecutor **Local** de Agent. El catálogo de esa etapa incluía `buses_en_ruta`, `estado_desvio`, `tiempo_llegada` y `reportar_desvio`. En E6, `estado_desvio` se integró en `buses_en_ruta`. El servidor no usa claves de API ni variables secretas.

## Las 5 consultas

Los resultados esperados provienen de llamadas al servidor con la flota ficticia de `flota_demo.py`. Las tres últimas columnas registran lo observado en Copilot.

| # | Consulta en lenguaje natural | Herramienta o primitiva esperada | Resultado esperado (servidor) | Herramienta que eligió el host | ¿Pidió permiso? | ¿Correcto? |
|---|---|---|---|---|---|---|
| 1 | ¿En cuántos minutos llega el próximo bus de la ruta 7 a Plaza de Armas? | `tiempo_llegada(R-07, Plaza de Armas)` | V1A-456 en 3 min (V2B-789 está desviado y no cuenta) | tiempo_llegada | No | Sí; V1A-456 en 3 min. V2B-789, desviado, no cuenta. |
| 2 | ¿Qué buses de la ruta 12 están en servicio? ¿Alguno está desviado? | `buses_en_ruta(R-12)` y `estado_desvio(R-12)` en E5 | V1A-321 (km 0,8) y V2B-654 (km 1,7). Ninguno desviado. | buses_en_ruta (optimizada E6) | No | Sí; V1A-321 y V2B-654, ambos a 0 m del trazado y no desviados. |
| 3 | Estoy en Puente Grau, ruta 7. ¿Cuánto falta? | `tiempo_llegada(R-07, Puente Grau)` | V1A-123 en 2 min (V1A-456 ya pasó el paradero) | tiempo_llegada | No | Sí; V1A-123 en 2 min. V1A-456 ya pasó el paradero. |
| 4 | Prompt `/mcp.rutasit.aviso_usuarios` con `R-07` y «bus V2B-789 desviado por la curva» | Prompt `aviso_usuarios` | Aviso de hasta 280 caracteres, sin inventar horarios | Prompt `aviso_usuarios`. Copilot también consultó `buses_en_ruta` y `estado_desvio`. | No | Sí. El aviso tuvo 248 caracteres e indicó que la hora de la próxima actualización no estaba confirmada. |
| 5 | Reporta el desvío del bus V2B-789 con la evidencia. | `reportar_desvio(V2B-789, ...)` | Crea `agentes/mcp/reportes/DESVIO-01.md` después de la aprobación | `reportar_desvio` | Sí; aprobación manual en Copilot. | Sí; creó `DESVIO-01.md` con 895,4 m de distancia al trazado (RF-04: >150 m). |

## Observaciones

Nota de coherencia: las filas 4–5 y las Figuras 9–10 documentan la corrida E5, con cuatro herramientas. Las filas 1–3 y 5 se revalidaron con el catálogo optimizado E6; allí `estado_desvio` ya está integrado en `buses_en_ruta`, por eso la consulta 2 usó una sola herramienta.

Las consultas 1–3 se ejecutaron en VS Code con Copilot Agent usando el servidor MCP rutasit. La consulta 1 llamó a `tiempo_llegada` y devolvió V1A-456 en 3 min; la 2 llamó a `buses_en_ruta` del catálogo optimizado E6 y devolvió V1A-321 y V2B-654, ambos a 0 m del trazado y no desviados; la 3 llamó a `tiempo_llegada` y devolvió V1A-123 en 2 min. En la consulta 4 se usó `aviso_usuarios` y se generó un aviso de 248 caracteres sin inventar la hora de actualización. En la consulta 5 Copilot pidió permiso; se aprobó esa llamada y el servidor creó `reportes/DESVIO-01.md` con una distancia de 895,4 m.
