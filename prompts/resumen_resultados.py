"""Resume un resultados.json de promptfoo y, con --exigir, valida que el reporte sirva.

Uso: python3 prompts/resumen_resultados.py <carpeta>/resultados.json [--exigir v3,v4]

Con --exigir falla (codigo distinto de 0) si:
  - el reporte esta vacio o no se puede leer;
  - alguna version exigida no aparece, le faltan casos del casos.yaml de esa carpeta, o tiene duplicados;
  - algun resultado trae un error de proveedor o de ejecucion (salvo R3/v1 de seguridad,
    ausencia documentada que solo se permite si v1 no se exige);
  - alguna version exigida no aprueba el 100 % de sus casos.
Los fallos de versiones NO exigidas (v1, v2: linea base) son esperados y solo se muestran.
"""
import collections
import json
import pathlib
import re
import sys

import yaml


def cargar(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def resumir(ruta):
    res = cargar(ruta)["results"]["results"]
    tabla = collections.defaultdict(dict)
    metr = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    errores, duplicados = [], []
    for x in res:
        v = re.search(r"(v\d+(?:\.\d+)*)\.txt", x["prompt"]["label"]).group(1)
        i = x["vars"]["id"]
        if i in tabla[v]:
            duplicados.append((v, i))
        comp = x["gradingResult"]["componentResults"] if x.get("gradingResult") else []
        # failureReason: 1 = fallo de una asercion (academico, esperado en v1/v2); 2 = error de ejecucion/proveedor
        err = (x.get("response") or {}).get("error") if x.get("failureReason") == 2 else None
        if x.get("failureReason") == 2 or not comp:
            errores.append((v, i, str(err or x.get("error") or "sin resultados de aserciones")[:100]))
        fallas = [c["assertion"].get("metric") for c in comp if not c["pass"]]
        if x.get("success") is not True and not fallas:
            fallas = ["success no es true"]
        tabla[v][i] = fallas
        for c in comp:
            m = c["assertion"].get("metric")
            metr[v][m][1] += 1
            metr[v][m][0] += int(c["pass"])
    return tabla, metr, errores, duplicados


def ids_esperados(ruta):
    casos = pathlib.Path(ruta).parent / "casos.yaml"
    with open(casos, encoding="utf-8") as f:
        return {c["vars"]["id"] for c in yaml.safe_load(f)}


def sin_dato_declarado(ruta, version, caso, error):
    """Única ausencia documentada: R3 contra v1 fue bloqueado y no se grabó."""
    return (pathlib.Path(ruta).parent.name == "seguridad" and version == "v1" and caso == "R3"
            and error == "Falta la grabacion seguridad/grabaciones/v1/R3.txt")


if __name__ == "__main__":
    ruta = sys.argv[1]
    exigidas = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[2] == "--exigir" else []
    tabla, metr, errores, duplicados = resumir(ruta)
    esperados = ids_esperados(ruta)
    problemas = []
    if not tabla:
        problemas.append("el reporte no tiene resultados")
    for v in sorted(tabla):
        sin_dato = {i for vv, i, e in errores if vv == v and sin_dato_declarado(ruta, vv, i, e)}
        evaluados = {i: f for i, f in tabla[v].items() if i not in sin_dato}
        ok = sum(1 for f in evaluados.values() if not f)
        n = len(evaluados)
        extra = f", {len(sin_dato)} sin dato (falta la grabacion: no cuenta ni como exito ni como fallo)" if sin_dato else ""
        print(f"{v}: {ok}/{n} evaluados = {100*ok/max(n,1):.1f}%{extra}")
        for i, f in sorted(tabla[v].items()):
            if f and i not in sin_dato: print("   ", i, "falla:", f)
        print("   por asercion:", {m: f"{a}/{b}" for m, (a, b) in sorted(metr[v].items())})
    for v in exigidas:
        if v not in tabla:
            problemas.append(f"falta la version {v} en el reporte"); continue
        faltan = esperados - set(tabla[v])
        sobran = set(tabla[v]) - esperados
        if faltan: problemas.append(f"{v}: faltan casos {sorted(faltan)}")
        if sobran: problemas.append(f"{v}: casos que no estan en casos.yaml {sorted(sobran)}")
        if any(f for i, f in tabla[v].items()):
            problemas.append(f"{v}: no aprueba el 100 %")
    if duplicados: problemas.append(f"resultados duplicados {duplicados}")
    for v, i, e in errores:
        if v in exigidas or not sin_dato_declarado(ruta, v, i, e):
            problemas.append(f"error de ejecucion en {v}/{i}: {e}")
    if problemas:
        sys.exit("REPORTE NO VALIDO:\n  - " + "\n  - ".join(problemas))
