"""Gráficos de E4, E5 y E7 a partir de trazas/*/metricas.json y resumen.json.
Uso (desde agentes/): python diagramas/metricas.py  ->  diagramas/img/*.png"""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "diagramas" / "img"
AZUL, NARANJA, GRIS = "#2a78d6", "#eb6834", "#b9b8b2"
TEXTO, TEXTO2, FONDO = "#0b0b0b", "#52514e", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": "#d8d7d2",
                     "axes.labelcolor": TEXTO2, "xtick.color": TEXTO2, "ytick.color": TEXTO2,
                     "figure.facecolor": FONDO, "axes.facecolor": FONDO})


def cargar():
    filas = {}
    for c in sorted((RAIZ / "trazas").iterdir()):
        if not (c / "metricas.json").exists():
            continue
        m = json.loads((c / "metricas.json").read_text(encoding="utf-8"))
        r = json.loads((c / "resumen.json").read_text(encoding="utf-8"))
        filas[c.name] = {
            "pasos": sum(v.get("pasos", 0) for v in m.values()),
            "acciones": sum(v.get("permitidas", 0) + v.get("bloqueadas", 0) for v in m.values()),
            "bloqueadas": sum(v.get("bloqueadas", 0) for v in m.values()),
            "contexto": sum(x["caracteres"] for x in r["contexto"]),
            "por_agente": [(x["agente"], x["caracteres"]) for x in r["contexto"]],
            "rondas": r["rondas"],
        }
    return filas


def _ejes(ax, titulo):
    ax.set_title(titulo, loc="left", fontsize=10.5, color=TEXTO, pad=8)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#ecebe7", linewidth=0.8)
    ax.set_axisbelow(True)


def barras(ax, etiquetas, valores, colores, titulo, fmt="{:,}"):
    y = range(len(etiquetas))
    ax.barh(list(y), valores, color=colores, height=0.55, edgecolor=FONDO, linewidth=2)
    ax.set_yticks(list(y), etiquetas)
    ax.invert_yaxis()
    tope = max(valores)
    for i, v in zip(y, valores):
        ax.text(v + tope * 0.02, i, fmt.format(v).replace(",", " "), va="center", fontsize=9, color=TEXTO)
    ax.set_xlim(0, tope * 1.18)
    _ejes(ax, titulo)


def grafico_e7(f):
    orden = ["issue1_unico", "issue2_unico", "issue2_coordinado", "issue3_unico", "issue3_unico_mapa"]
    nombres = ["Issue 1 · único", "Issue 2 · único", "Issue 2 · actor-crítico", "Issue 3 · único",
               "Issue 3 · único + mapa/notas"]
    colores = [NARANJA if "coordinado" in o else AZUL for o in orden]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.4))
    barras(a, nombres, [f[o]["pasos"] for o in orden], colores, "Pasos del bucle (todas las rondas)")
    barras(b, ["", "", "", "", ""], [f[o]["contexto"] for o in orden], colores, "Contexto final (caracteres, suma de agentes)")
    fig.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=AZUL), plt.Rectangle((0, 0), 1, 1, color=NARANJA)],
               labels=["Agente único", "Planificador + ejecutor + revisor"], loc="lower center", ncol=2,
               frameon=False, fontsize=9)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(SALIDA / "e7_metricas_issues.png", dpi=180)


def grafico_e5(f):
    u, c = f["issue2_unico"], f["issue2_coordinado"]
    fig, ejes = plt.subplots(1, 3, figsize=(10, 2.6))
    for ax, clave, titulo in zip(ejes, ("pasos", "acciones", "contexto"),
                                 ("Pasos", "Acciones con herramientas", "Contexto final (caracteres)")):
        barras(ax, ["Único", "Actor-crítico"], [u[clave], c[clave]], [AZUL, NARANJA], titulo)
    fig.tight_layout()
    fig.savefig(SALIDA / "e5_unico_vs_actor_critico.png", dpi=180)


def grafico_e4(f):
    orden = ["issue1_unico", "issue3_unico", "issue3_unico_mapa"]
    nombres = ["E2 · issue 1 (básicas)", "Issue 3 (básicas)", "Issue 3 (mapa_repo + notas)"]
    colores = [GRIS, AZUL, NARANJA]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 2.6))
    barras(a, nombres, [f[o]["pasos"] for o in orden], colores, "Pasos")
    barras(b, ["", "", ""], [f[o]["contexto"] for o in orden], colores, "Contexto final (caracteres)")
    fig.tight_layout()
    fig.savefig(SALIDA / "e4_herramienta_y_memoria.png", dpi=180)


if __name__ == "__main__":
    SALIDA.mkdir(parents=True, exist_ok=True)
    datos = cargar()
    grafico_e7(datos); grafico_e5(datos); grafico_e4(datos)
    print(json.dumps({k: {x: v[x] for x in ("pasos", "acciones", "bloqueadas", "contexto", "rondas")}
                      for k, v in datos.items()}, ensure_ascii=False, indent=1))
