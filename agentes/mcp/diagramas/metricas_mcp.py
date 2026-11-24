"""E6: gráficos del costo del catálogo y de la latencia, desde trazas/analista_catalogo_v*/metricas.json.
Uso (desde agentes/mcp): python diagramas/metricas_mcp.py  ->  diagramas/img/*.png"""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "diagramas" / "img"
AZUL, NARANJA, TEXTO, TEXTO2, FONDO, REJILLA = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#fcfcfb", "#ecebe7"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": "#d8d7d2",
                     "axes.labelcolor": TEXTO2, "xtick.color": TEXTO2, "ytick.color": TEXTO2,
                     "figure.facecolor": FONDO, "axes.facecolor": FONDO})


def cargar(n):
    return json.loads((RAIZ / "trazas" / f"analista_catalogo_v{n}" / "metricas.json").read_text(encoding="utf-8"))


def _ejes(ax, titulo):
    ax.set_title(titulo, loc="left", fontsize=10.5, color=TEXTO, pad=8)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)


def grafico_catalogo(v1, v2):
    nombres = list(v1["tokens_catalogo"])
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.0), gridspec_kw={"width_ratios": [1.6, 1]})
    y = range(len(nombres))
    a.barh([i - 0.19 for i in y], [v1["tokens_catalogo"][n] for n in nombres], height=0.36, color=AZUL,
           edgecolor=FONDO, linewidth=2, label="Catálogo v1 (E2)")
    a.barh([i + 0.19 for i in y], [v2["tokens_catalogo"].get(n, 0) for n in nombres], height=0.36, color=NARANJA,
           edgecolor=FONDO, linewidth=2, label="Catálogo v2 (E6)")
    for i, n in zip(y, nombres):
        a.text(v1["tokens_catalogo"][n] + 6, i - 0.19, f"{v1['tokens_catalogo'][n]}", va="center", fontsize=8.5)
        v = v2["tokens_catalogo"].get(n)
        a.text((v or 0) + 6, i + 0.19, f"{v}" if v else "fusionada en buses_en_ruta", va="center", fontsize=8.5,
               color=TEXTO if v else TEXTO2)
    a.set_yticks(list(y), nombres)
    a.invert_yaxis()
    a.set_xlim(0, max(v1["tokens_catalogo"].values()) * 1.45)
    a.legend(frameon=False, fontsize=8.5, loc="lower right")
    _ejes(a, "Tokens por herramienta en tools/list (≈ caracteres / 4)")
    tot = [v1["tokens_catalogo_total"], v2["tokens_catalogo_total"]]
    b.barh([0, 1], tot, color=[AZUL, NARANJA], height=0.5, edgecolor=FONDO, linewidth=2)
    b.set_yticks([0, 1], ["v1", "v2"])
    b.invert_yaxis()
    for i, t in enumerate(tot):
        b.text(t + 15, i, f"{t}", va="center", fontsize=9)
    b.set_xlim(0, max(tot) * 1.3)
    _ejes(b, f"Catálogo completo: −{100 * (tot[0] - tot[1]) / tot[0]:.0f} %")
    fig.tight_layout()
    fig.savefig(SALIDA / "e6_costo_catalogo.png", dpi=180)


def grafico_latencia(v2):
    metodos = list(v2["latencia_ms"])
    medias = [sum(v2["latencia_ms"][m]) / len(v2["latencia_ms"][m]) for m in metodos]
    fig, ax = plt.subplots(figsize=(10, 2.4))
    ax.barh(range(len(metodos)), medias, color=AZUL, height=0.5, edgecolor=FONDO, linewidth=2)
    ax.set_xscale("log")
    ax.set_yticks(range(len(metodos)), [f"{m} ({len(v2['latencia_ms'][m])})" for m in metodos])
    ax.invert_yaxis()
    for i, v in enumerate(medias):
        ax.text(v * 1.12, i, f"{v:.1f} ms", va="center", fontsize=9)
    ax.set_xlim(0.8, max(medias) * 4)
    _ejes(ax, "Latencia media por método JSON-RPC, stdio (escala log; entre paréntesis, n.º de llamadas)")
    fig.tight_layout()
    fig.savefig(SALIDA / "e6_latencia.png", dpi=180)


if __name__ == "__main__":
    SALIDA.mkdir(parents=True, exist_ok=True)
    v1, v2 = cargar(1), cargar(2)
    grafico_catalogo(v1, v2)
    grafico_latencia(v2)
    print({"v1": v1["tokens_catalogo_total"], "v2": v2["tokens_catalogo_total"]})
