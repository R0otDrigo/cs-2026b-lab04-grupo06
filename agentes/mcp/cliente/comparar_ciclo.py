"""E6: captura el inicio de la conexión de un cliente actual (2026-07-28, sin sesión) y de uno antiguo
(forzado con mode="legacy": initialize de 2025) contra el mismo servidor, ambos a través del espía.
Uso (desde agentes/mcp): python cliente/comparar_ciclo.py"""
import asyncio, json, os, pathlib, sys
from mcp import Client, StdioServerParameters

RAIZ = pathlib.Path(__file__).resolve().parents[1]


async def capturar(nombre, **opciones):
    traza = RAIZ / "trazas" / nombre / "mcp_trafico.jsonl"
    traza.parent.mkdir(parents=True, exist_ok=True)
    traza.unlink(missing_ok=True)
    srv = StdioServerParameters(command=sys.executable, env={**os.environ, "MCP_TRAZA": str(traza)},
                                args=[str(RAIZ / "cliente/espia.py"), str(RAIZ / "servidor_mcp/rutasit_mcp.py")])
    async with Client(srv, **opciones) as c:
        await c.list_tools()
        await c.call_tool("tiempo_llegada", {"ruta": "R-07", "paradero": "Plaza de Armas"})
        version = c.protocol_version
    metodos = [json.loads(l)["msg"].get("method") for l in traza.read_text(encoding="utf-8").splitlines()
               if json.loads(l)["dir"] == "host->servidor"]
    print(f"{nombre:<16} protocolo {version}: {' -> '.join(metodos)}")


async def main():
    await capturar("cliente_actual")
    await capturar("cliente_antiguo", mode="legacy")

asyncio.run(main())
