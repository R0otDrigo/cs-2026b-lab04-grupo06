"""Convierte el tráfico JSON-RPC capturado por el espía en un diagrama de secuencia Mermaid y en métricas
(mensajes, bytes, errores, latencia por método y tokens del catálogo de herramientas).
Uso (desde agentes/mcp): python cliente/traza_mcp.py trazas/analista"""
import collections, json, pathlib, sys

APROBAR = ("reportar_desvio",)


def cargar(archivo):
    return [json.loads(l) for l in open(archivo, encoding="utf-8") if l.strip()]


def _texto_resultado(r) -> str:
    sc = r.get("structuredContent")
    if isinstance(sc, dict) and "mensaje" in sc:
        return sc["mensaje"][:40]
    if isinstance(sc, dict) and isinstance(sc.get("result"), list):
        return f"{len(sc['result'])} elementos"
    if isinstance(sc, dict) and isinstance(sc.get("result"), str):
        return sc["result"][:40]
    return "resultado"


def a_mermaid(eventos) -> str:
    l = ["sequenceDiagram", "    autonumber", "    actor U as Humano", "    participant A as Agente (host MCP)",
         "    participant S as Servidor MCP rutasit"]
    pendientes = {}
    for e in eventos:
        m = e["msg"]
        if e["dir"] == "host->servidor" and "method" in m:
            p = m.get("params") or {}
            nombre = p.get("name") or p.get("uri") or ""
            if nombre in APROBAR:
                l += [f"    A->>U: ¿apruebas {nombre}?", "    U-->>A: s"]
            pendientes[m.get("id")] = m["method"]
            l.append(f"    A->>S: {m['method']} {nombre}".rstrip())
        elif e["dir"] == "servidor->host" and "id" in m:
            r = m.get("result", {})
            if "error" in m or r.get("isError"):
                texto = (r.get("content") or [{}])[0].get("text", "") if r else m["error"].get("message", "")
                l.append(f"    S--xA: isError: {texto.split(': ', 1)[-1].split('. ')[0][:45].replace(';', ',')}")
            elif pendientes.get(m["id"]) == "server/discover":
                l.append(f"    S-->>A: versiones {', '.join(r.get('supportedVersions', []))} + capacidades")
            elif "tools" in r:
                l.append(f"    S-->>A: {len(r['tools'])} herramientas con esquema")
            elif "contents" in r:
                l.append("    S-->>A: contenido del recurso")
            else:
                l.append(f"    S-->>A: {_texto_resultado(r).replace(';', ',')}")
    return "\n".join(l)


def tokens_catalogo(eventos) -> dict:
    """~tokens (caracteres / 4) de cada herramienta tal como viaja en tools/list."""
    for e in eventos:
        r = e["msg"].get("result", {}) if e["dir"] == "servidor->host" else {}
        if "tools" in r:
            return {t["name"]: len(json.dumps(t, ensure_ascii=False)) // 4 for t in r["tools"]}
    return {}


def metricas(eventos) -> dict:
    envios = {e["msg"]["id"]: e for e in eventos if e["dir"] == "host->servidor" and "id" in e["msg"]}
    lat = collections.defaultdict(list)
    errores = 0
    for e in eventos:
        m = e["msg"]
        if e["dir"] == "servidor->host" and m.get("id") in envios:
            ida = envios[m["id"]]
            lat[ida["msg"]["method"]].append(round((e["t"] - ida["t"]) * 1000, 1))
            errores += bool(m.get("result", {}).get("isError") or "error" in m)
    tok = tokens_catalogo(eventos)
    return {"mensajes": len(eventos), "bytes": sum(len(json.dumps(e["msg"], ensure_ascii=False)) for e in eventos),
            "errores": errores, "latencia_ms": dict(lat), "tokens_catalogo": tok,
            "tokens_catalogo_total": sum(tok.values())}


if __name__ == "__main__":
    carpeta = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "trazas/analista")
    ev = cargar(carpeta / "mcp_trafico.jsonl")
    (carpeta / "mcp_trafico.mmd").write_text(a_mermaid(ev) + "\n", encoding="utf-8")
    print(json.dumps(metricas(ev), ensure_ascii=False, indent=1))
