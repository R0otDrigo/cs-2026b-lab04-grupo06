"""Auditor básico de servidores MCP: revisa el catálogo ANTES de conectarlo a un host.
Uso (desde agentes/mcp): python cliente/auditar.py servidor_mcp/rutasit_mcp.py terceros/clima_mcp.py
Código de salida 1 si algún servidor tiene hallazgos de severidad ALTA.

Reglas del docente: instrucciones ocultas, secretos, comandos o URL, lectura ajena, parámetros genéricos,
sin anotaciones y descripción muy larga. Reglas nuevas del Grupo 06 (E7):
  R-G06-1: herramienta de ESCRITURA sin destructiveHint explícito (el host no sabe si puede borrar).
  R-G06-2: parámetro de texto libre sin maxLength (puede usarse para sacar datos o inflar el contexto).
"""
import asyncio, re, sys
from mcp import Client, StdioServerParameters

REGLAS = [  # (severidad, patrón en la descripción, explicación)
    ("ALTA", r"<\s*important\s*>|ignora|ignore (all|previous)|no (le )?(menciones|digas)|do not (tell|mention)",
     "instrucciones ocultas dirigidas al modelo"),
    ("ALTA", r"\.env\b|id_rsa|\.ssh|credencial|password|contraseña|token|api[_ ]?key", "pide secretos o credenciales"),
    ("ALTA", r"curl |wget |\| *sh\b|https?://", "comandos o URL externas en la descripción"),
    ("MEDIA", r"(lee|read).{0,40}(archivo|file|recurso|resource)", "pide leer datos ajenos a su función"),
]
PARAMS_SOSPECHOSOS = {"contexto", "context", "notas", "notes", "extra", "metadata", "debug"}


def _anot(t, campo):
    a = t.get("annotations") or {}
    return a.get(campo)


def revisar(tools: list[dict]) -> list[tuple]:
    """Revisa definiciones de herramientas como viajan en tools/list (dicts con camelCase)."""
    hallazgos = []
    for t in tools:
        nombre, desc = t["name"], t.get("description") or ""
        props = (t.get("inputSchema") or {}).get("properties", {})
        for sev, patron, motivo in REGLAS:
            if re.search(patron, desc, re.I):
                hallazgos.append((sev, nombre, motivo))
        for p in sorted(set(props) & PARAMS_SOSPECHOSOS):
            hallazgos.append(("MEDIA", nombre, f"parámetro genérico '{p}' que podría usarse para filtrar datos"))
        if not t.get("annotations"):
            hallazgos.append(("BAJA", nombre, "sin anotaciones (¿solo lectura? ¿destructiva?)"))
        elif _anot(t, "readOnlyHint") is not True and _anot(t, "destructiveHint") is None:      # R-G06-1
            hallazgos.append(("MEDIA", nombre, "escritura sin destructiveHint explícito"))
        for p, esquema in sorted(props.items()):                                               # R-G06-2
            if esquema.get("type") == "string" and "maxLength" not in esquema and "enum" not in esquema:
                hallazgos.append(("MEDIA", nombre, f"parámetro de texto '{p}' sin maxLength"))
        if len(desc) > 400:
            hallazgos.append(("BAJA", nombre, f"descripción muy larga ({len(desc)} caracteres)"))
    return hallazgos


async def auditar(ruta) -> bool:
    async with Client(StdioServerParameters(command=sys.executable, args=[ruta])) as c:
        tools = [t.model_dump(by_alias=True, exclude_none=True, mode="json") for t in (await c.list_tools()).tools]
        print(f"Servidor: {c.server_info.name}  ({len(tools)} herramientas)")
    hallazgos = revisar(tools)
    for h in hallazgos or [("OK", "-", "sin hallazgos")]:
        print(f"  [{h[0]:<5}] {h[1]:<20} {h[2]}")
    return any(h[0] == "ALTA" for h in hallazgos)


if __name__ == "__main__":
    altos = [asyncio.run(auditar(r)) for r in sys.argv[1:]]
    sys.exit(1 if any(altos) else 0)
