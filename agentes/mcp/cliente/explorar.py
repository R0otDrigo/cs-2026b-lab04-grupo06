"""Host MCP mínimo: descubre las capacidades del servidor rutasit y prueba cada primitiva.
Uso (desde agentes/mcp): python cliente/explorar.py     (pasa por el espía: trazas/explorar.jsonl)"""
import asyncio, json, os, pathlib, sys
from mcp import Client, StdioServerParameters
from mcp.types import Implementation

RAIZ = pathlib.Path(__file__).resolve().parents[1]
TRAZA = RAIZ / "trazas" / "explorar.jsonl"
SERVIDOR = StdioServerParameters(command=sys.executable,
                                 args=[str(RAIZ / "cliente/espia.py"), str(RAIZ / "servidor_mcp/rutasit_mcp.py")],
                                 env={**os.environ, "MCP_TRAZA": str(TRAZA)})


def texto(resultado) -> str:
    return " ".join(getattr(c, "text", "") for c in resultado.content)


async def main():
    TRAZA.unlink(missing_ok=True)
    async with Client(SERVIDOR, client_info=Implementation(name="explorador-lab11", version="1.0")) as c:
        print(f"Servidor: {c.server_info.name} | protocolo {c.protocol_version}")
        herramientas = (await c.list_tools()).tools
        print("\nHERRAMIENTAS (las elige el modelo):")
        for h in herramientas:
            a = h.annotations
            tipo = "solo lectura" if a and a.read_only_hint else "ESCRITURA"
            print(f"  - {h.name}({', '.join(h.input_schema.get('properties', {}))})  [{tipo}]")
        print("\nRECURSOS (los elige la aplicación):")
        for r in (await c.list_resources()).resources:
            print(f"  - {r.uri}  {r.title}")
        for t in (await c.list_resource_templates()).resource_templates:
            print(f"  - {t.uri_template}  {t.title} (plantilla)")
        print("\nPROMPTS (los elige el usuario):")
        for p in (await c.list_prompts()).prompts:
            print(f"  - {p.name}({', '.join(a.name for a in p.arguments or [])})")

        print("\nPRUEBAS DE USO:")
        r = await c.call_tool("tiempo_llegada", {"ruta": "R-07", "paradero": "Plaza de Armas"})
        print("  tiempo_llegada(R-07, Plaza de Armas) →", json.dumps(r.structured_content, ensure_ascii=False))
        r = await c.call_tool("tiempo_llegada", {"ruta": "R-07", "paradero": "Puente Grau"})
        print("  tiempo_llegada(R-07, Puente Grau)    →", r.structured_content["mensaje"])
        r = await c.call_tool("buses_en_ruta", {"ruta": "7"})
        print("  buses_en_ruta(7) → is_error =", r.is_error, "|", texto(r)[:95])
        r = await c.read_resource("rutasit://adr/010")
        print("  read_resource(adr/010) →", r.contents[0].text.splitlines()[0])
        r = await c.get_prompt("aviso_usuarios", {"ruta": "R-07", "situacion": "bus V2B-789 desviado"})
        print("  get_prompt(aviso_usuarios) →", r.messages[0].content.text[:70], "…")


asyncio.run(main())
