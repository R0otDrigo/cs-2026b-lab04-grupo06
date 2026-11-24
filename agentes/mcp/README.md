# Servidor MCP de RutaSIT (Laboratorio 11)

```text
pip install -r requirements.txt                          # desde la raíz; incluye mcp>=2
pip install matplotlib                                  # opcional: regenerar los gráficos de E6
cd agentes/mcp
python -m pytest -q pruebas                              # contrato, adaptador, auditor y corrida grabada (25)
python cliente/explorar.py                               # host mínimo: descubre y prueba cada primitiva
python analista_mcp.py                                   # agente del Lab 10 vía MCP (reproduce la corrida grabada)
python analista_mcp.py --interactivo --humano consola    # graba una corrida nueva con su asistente
python cliente/traza_mcp.py trazas/analista_catalogo_v2  # diagrama Mermaid + métricas del tráfico
python cliente/comparar_ciclo.py                         # cliente 2026-07-28 frente a cliente antiguo
python cliente/auditar.py servidor_mcp/rutasit_mcp.py terceros/clima_mcp.py
python diagramas/metricas_mcp.py                         # gráficos de E6
npx @modelcontextprotocol/inspector python servidor_mcp/rutasit_mcp.py
```

| Carpeta o archivo | Contenido |
|---|---|
| `servidor_mcp/rutasit_mcp.py`, `flota_demo.py` | Servidor (E2) y datos ficticios de la flota |
| `diseno/` | Catálogo (E1) y arquitectura |
| `pruebas/` | Pruebas de contrato (E3), del adaptador (E4), del auditor (E7) y de la corrida; `inspector.md` |
| `cliente/` | Espía de stdio, explorador, traza del protocolo, auditor y comparación de ciclos |
| `analista_mcp.py`, `trayectorias/`, `trazas/` | Agente del Lab 10 vía MCP (E4) y su evidencia |
| `uso-en-host.md`, `protocolo.md`, `seguridad.md`, `bitacora-ia.md`, `cuestionario.md` | E5, E6, E7 y cuestionario |
| `terceros/clima_mcp.py` | Servidor envenenado de los recursos del curso. **No conectarlo a un host real.** |

El adaptador `HerramientasMCP` y la política ampliada están en `agentes/agente/` junto al resto del framework del Lab 10.
