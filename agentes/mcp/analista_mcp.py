"""E4: el agente del Lab 10, sin cambios en su núcleo, resolviendo una consulta de RutaSIT con las
herramientas que descubre en el servidor MCP. Todo el tráfico pasa por el espía.

Uso (desde agentes/mcp):
  python analista_mcp.py --interactivo --humano consola     # graba decisiones (asistente) y respuestas (humano)
  python analista_mcp.py                                    # reproduce la corrida grabada (ModeloGrabado)
Cada corrida deja: trayectorias/<corrida>/ (decisiones y humano.json) y trazas/<corrida>/ (agente.jsonl,
mcp_trafico.jsonl, mcp_trafico.mmd, metricas.json y los reportes creados en una carpeta propia).
"""
import argparse, json, os, pathlib, shutil, sys

AQUI = pathlib.Path(__file__).resolve().parent
sys.path[:0] = [str(AQUI.parent), str(AQUI / "cliente")]           # agentes/ (framework del Lab 10) y cliente/

from mcp import StdioServerParameters                                  # noqa: E402
from agente.nucleo import Agente                                       # noqa: E402
from agente.modelos import ModeloGrabado, ModeloInteractivo, PROTOCOLO  # noqa: E402
from agente.politica import Politica                                   # noqa: E402
from agente.humano import AprobadorConsola, AprobadorGrabado           # noqa: E402
from agente.herramientas_mcp import HerramientasMCP                    # noqa: E402
import traza_mcp                                                       # noqa: E402

CONSULTA = ("Un pasajero espera en el paradero Plaza de Armas y pregunta en cuántos minutos llega el próximo bus "
            "de la ruta 7 (Cerro Colorado - Centro). El centro de control también quiere saber si algún bus de esa "
            "ruta está desviado; si lo está, repórtalo con la evidencia.")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corrida", default="analista_catalogo_v1")
    ap.add_argument("--interactivo", action="store_true")
    ap.add_argument("--humano", choices=("consola", "grabado"), default="grabado")
    a = ap.parse_args(argv)

    tray, traz = AQUI / "trayectorias" / a.corrida, AQUI / "trazas" / a.corrida
    tray.mkdir(parents=True, exist_ok=True)
    traz.mkdir(parents=True, exist_ok=True)                # se conserva mcp_trafico.png si ya existe
    shutil.rmtree(traz / "reportes", ignore_errors=True)
    for f in ("mcp_trafico.jsonl", "agente.jsonl"):
        (traz / f).unlink(missing_ok=True)
    entorno = {**os.environ, "MCP_TRAZA": str(traz / "mcp_trafico.jsonl"), "RUTASIT_REPORTES": str(traz / "reportes")}
    h = HerramientasMCP(StdioServerParameters(
        command=sys.executable, args=[str(AQUI / "cliente/espia.py"), str(AQUI / "servidor_mcp/rutasit_mcp.py")],
        env=entorno))
    try:
        escritura = h.herramientas_de_escritura()
        print("Herramientas descubiertas por MCP:", ", ".join(h.catalogo()))
        print("Requieren aprobación (según anotaciones):", ", ".join(sorted(escritura)))
        aprobador = (AprobadorConsola(grabar_en=tray / "humano.json") if a.humano == "consola"
                     else AprobadorGrabado(tray / "humano.json"))
        politica = Politica(herramientas_permitidas=set(h.catalogo()), max_pasos=10,
                            requieren_aprobacion=escritura, aprobar=aprobador.accion)
        catalogo = "\n".join(f"- {k}: {v}" for k, v in h.catalogo().items())
        modelo = (ModeloInteractivo(str(tray / "analista.json")) if a.interactivo
                  else ModeloGrabado(tray / "analista.json"))
        agente = Agente("analista", modelo, h, politica,
                        f"{CONSULTA}\nHerramientas (servidor MCP rutasit):\n{catalogo}\n{PROTOCOLO}",
                        str(traz / "agente.jsonl"))
        respuesta = agente.ejecutar()
        contexto = len(json.dumps(agente.historial, ensure_ascii=False))
    finally:
        h.cerrar()

    eventos = traza_mcp.cargar(traz / "mcp_trafico.jsonl")
    (traz / "mcp_trafico.mmd").write_text(traza_mcp.a_mermaid(eventos) + "\n", encoding="utf-8")
    met = traza_mcp.metricas(eventos)
    met.update({"pasos_agente": len([e for e in agente.eventos if e["tipo"] in ("accion", "final")]),
                "contexto_agente_caracteres": contexto})
    (traz / "metricas.json").write_text(json.dumps(met, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nRESPUESTA:\n" + respuesta)
    for e in agente.eventos:
        if e["tipo"] == "accion":
            extra = f" humano={e['humano']}" if "humano" in e else ""
            print(f"  paso {e['paso']}: {e['accion']:<16} {e['estado']:<12}{extra} {e['observacion'][:70]!r}")
    print(json.dumps(met, ensure_ascii=False))
    return met


if __name__ == "__main__":
    main()
