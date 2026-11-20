"""Orquestador del sistema agéntico de RutaSIT (adaptado del mini framework del Lab 10).

Modo actual: unico -> un solo agente ejecutor (ReAct) con las herramientas básicas.

Ejemplos (desde la carpeta agentes/):
  python orquestador.py --issue 1 --modo unico --interactivo        # E2: graba con su asistente de IA
  python orquestador.py --issue 1 --modo unico                      # reproduce la trayectoria grabada
Cada corrida parte de una copia limpia de trabajo_original/ y deja su traza en trazas/<corrida>/.
"""
import argparse, json, pathlib, shutil, sys

RAIZ = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))

from agente.nucleo import Agente                                         # noqa: E402
from agente.herramientas import Herramientas                             # noqa: E402
from agente.modelos import ModeloGrabado, ModeloInteractivo, PROTOCOLO   # noqa: E402
from agente.politica import Politica                                     # noqa: E402
from agente import traza                                                 # noqa: E402



def nombre_corrida(a):
    n = f"issue{a.issue}_{a.modo}"
    return a.corrida or n


def catalogo_de(h, permitidas):
    return "\n".join(f"- {d}" for k, d in h.catalogo().items() if k in permitidas)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--issue", type=int, choices=(1, 2, 3), required=True)
    ap.add_argument("--modo", choices=("unico",), default="unico")
    ap.add_argument("--interactivo", action="store_true", help="pedir cada decisión a su asistente de IA y grabarla")
    ap.add_argument("--corrida", help="nombre de la carpeta en trayectorias/ y trazas/")
    a = ap.parse_args(argv)

    corrida = nombre_corrida(a)
    tray_dir, traza_dir = RAIZ / "trayectorias" / corrida, RAIZ / "trazas" / corrida
    tray_dir.mkdir(parents=True, exist_ok=True)
    shutil.rmtree(traza_dir, ignore_errors=True)
    traza_dir.mkdir(parents=True)
    trabajo = RAIZ / "trabajo"
    shutil.rmtree(trabajo, ignore_errors=True)                           # cada corrida parte del estado original
    shutil.copytree(RAIZ / "trabajo_original", trabajo, ignore=shutil.ignore_patterns("__pycache__"))
    h = Herramientas(trabajo)
    issue = f"issues/ISSUE-0{a.issue}.md"

    def modelo(nombre):
        archivo = tray_dir / f"{nombre}.json"
        return ModeloInteractivo(str(archivo)) if a.interactivo else ModeloGrabado(archivo)

    permitidas_ejecutor = set(h.catalogo()) - {"ver_cambios"}
    reglas = ("Reglas: trabaja solo dentro del repositorio; no modifiques test/ ni tests/; corrige la causa "
              "en src/rutasit; termina cuando la prueba del issue pase sin regresiones.")
    objetivo = (f"Resuelve {issue} del repositorio RutaSIT Arequipa (código en src/rutasit).\n" + reglas
                + f"\nHerramientas:\n{catalogo_de(h, permitidas_ejecutor)}\n{PROTOCOLO}")
    ej = Agente("ejecutor", modelo("ejecutor"), h,
                Politica(herramientas_permitidas=permitidas_ejecutor, max_pasos=12),
                objetivo, str(traza_dir / "ejecutor.jsonl"))
    resumen = ej.ejecutar()
    agentes = [ej]
    print(f"EJECUTOR: {resumen}")

    # Evidencia de la corrida: diff, notas, pruebas finales y tamaño del contexto de cada agente.
    (traza_dir / "cambios.diff").write_text(h.ver_cambios() + "\n", encoding="utf-8")
    if (trabajo / "notas.md").exists():
        shutil.copy(trabajo / "notas.md", traza_dir / "notas.md")
    datos = {
        "corrida": corrida, "issue": a.issue, "modo": a.modo, "herramientas": "basicas",
        "humano": "no", "rondas": 1,
        "veredicto": "", "pruebas_finales": h.ejecutar_pruebas(),
        "contexto": [{"agente": x.nombre, "caracteres": len(json.dumps(x.historial, ensure_ascii=False))}
                     for x in agentes],
    }
    (traza_dir / "resumen.json").write_text(json.dumps(datos, ensure_ascii=False, indent=1), encoding="utf-8")
    traza.generar(traza_dir)
    print(f"Pruebas al final: {datos['pruebas_finales']}")
    for c in datos["contexto"]:
        print(f"[{c['agente']}] contexto final: {c['caracteres']} caracteres (~{c['caracteres'] // 4} tokens)")
    print("Decisión final: HUMANO (aprobar o rechazar el Pull Request).")
    return datos


if __name__ == "__main__":
    main()
