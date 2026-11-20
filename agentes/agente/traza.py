"""Observabilidad: convierte las trazas JSONL de una corrida en un diagrama de secuencia (Mermaid)
y en métricas. Uso: python agente/traza.py trazas/issue1_unico   (o sin argumento: todas las corridas)."""
import collections, json, pathlib, re, shutil, subprocess, sys

ORDEN = ["planificador", "ejecutor", "revisor", "ejecutor_r2", "revisor_r2", "ejecutor_r3", "revisor_r3"]


def cargar(carpeta):
    eventos = []
    for n in ORDEN:
        f = pathlib.Path(carpeta) / f"{n}.jsonl"
        if f.exists():
            ronda = int(n.split("_r")[1]) if "_r" in n else 1
            with open(f, encoding="utf-8") as fh:
                eventos += [dict(json.loads(l), ronda=ronda) for l in fh if l.strip()]
    return eventos


def _limpio(t: str, n=42) -> str:
    return t.replace(";", ",").replace("#", "N.").replace(":", " ").replace('"', "'")[:n]


def resumir(e) -> str:
    obs, acc, args = e["observacion"], e["accion"], e["args"]
    if acc == "leer_archivo": return f"contenido de {str(args.get('ruta', '')).split('/')[-1]}"
    if acc == "buscar": return "sin resultados" if "sin resultados" in obs else f"{len(obs.splitlines())} coincidencia(s)"
    if acc == "ver_cambios": return f"diff de {len(obs.splitlines())} líneas"
    if acc == "mapa_repo": return f"mapa de {sum(1 for l in obs.splitlines() if not l.startswith(' '))} módulos"
    if acc in ("anotar", "leer_notas"): return _limpio(obs.splitlines()[0] if obs else "")
    if acc == "ejecutar_comando" and str(args.get("comando", "")).startswith("radon"):
        grados = sorted(set(re.findall(r" - ([A-F]) \(", obs)))
        return "complejidad " + ("/".join(grados) or "?")
    if acc in ("ejecutar_comando", "ejecutar_pruebas"):
        resumen = [l for l in obs.splitlines() if re.search(r"\d+ (passed|failed|error)", l)]
        if resumen:
            return _limpio(re.sub(r" in [\d.]+s", "", resumen[-1].replace("=", "")).strip())  # sin tiempos
    if acc == "editar_archivo" and obs.startswith("OK"): return "OK, archivo modificado"
    return _limpio((obs.strip().splitlines() or [""])[-1])


def a_mermaid(eventos) -> str:
    alias = {"planificador": "PL", "ejecutor": "EJ", "revisor": "RV"}
    presentes = {e["agente"] for e in eventos}
    l = ["sequenceDiagram", "    autonumber", "    actor U as Humano"]
    if "planificador" in presentes: l.append("    participant PL as Planificador")
    l.append("    participant EJ as Ejecutor (actor)" if "revisor" in presentes else "    participant EJ as Agente ReAct")
    if "revisor" in presentes: l.append("    participant RV as Revisor (crítico)")
    l += ["    participant P as Política", "    participant H as Herramientas"]
    ronda_actual = 1
    for e in eventos:
        a = alias[e["agente"]]
        if e["ronda"] != ronda_actual:
            ronda_actual = e["ronda"]
            l.append(f"    Note over EJ,RV: Ronda {ronda_actual} del bucle actor-crítico")
        if e["tipo"] == "objetivo":
            if a == "PL" or ("planificador" not in presentes and a == "EJ" and e["ronda"] == 1):
                l.append(f"    U->>{a}: objetivo (issue)")
            elif a == "EJ":
                l.append(f"    {'PL' if e['ronda'] == 1 else 'RV'}->>EJ: {'plan' if e['ronda'] == 1 else 'cambios solicitados'}")
            else:
                l.append("    EJ->>RV: resumen + diff")
        elif e["tipo"] == "accion":
            if e["estado"] == "CONTRATO_INVALIDO":
                l += [f"    {a}-x{a}: decisión fuera de contrato"]
            elif "humano" in e:
                l += [f"    {a}->>U: ¿aprobar {e['accion']}?", f"    U-->>{a}: {e['humano']}"]
                l += ([f"    {a}->>H: {e['accion']}", f"    H-->>{a}: {resumir(e)}"] if not e["bloqueada"] else [])
            elif e["bloqueada"]:
                l += [f"    {a}-xP: {e['accion']}", f"    P--x{a}: BLOQUEADO"]
            else:
                l += [f"    {a}->>H: {e['accion']}", f"    H-->>{a}: {resumir(e)}"]
        elif e["tipo"] == "final":
            if a == "PL":
                pass
            elif a == "RV" and not e["texto"].startswith("CAMBIOS"):
                l.append(f"    RV-->>U: {_limpio(e['texto'].split('.')[0])}")
            elif a == "EJ" and "revisor" not in presentes:
                l.append("    EJ-->>U: resumen final (el humano revisa el PR)")
    return "\n".join(l)


def metricas(eventos) -> dict:
    m = collections.defaultdict(collections.Counter)
    for e in eventos:
        nombre = e["agente"] + ("" if e["ronda"] == 1 else f"_r{e['ronda']}")
        if e["tipo"] == "accion":
            m[nombre]["pasos"] += 1
            if e["estado"] == "CONTRATO_INVALIDO":
                m[nombre]["contrato_rechazado"] += 1
            elif e["bloqueada"]:
                m[nombre]["bloqueadas"] += 1
            else:
                m[nombre]["permitidas"] += 1
            if e["accion"] != "(ninguna)":
                m[nombre]["herr:" + e["accion"]] += 1
        elif e["tipo"] == "final":
            m[nombre]["pasos"] += 1
    return {k: dict(v) for k, v in m.items()}


def renderizar_png(mmd: pathlib.Path) -> bool:
    """Intenta renderizar con mermaid-cli (mmdc). Si no está instalado, deja solo el .mmd."""
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return False
    r = subprocess.run([mmdc, "-i", str(mmd), "-o", str(mmd.with_suffix(".png")), "-b", "white", "-s", "2"],
                       capture_output=True, text=True)
    return r.returncode == 0


def generar(carpeta, png=False):
    carpeta = pathlib.Path(carpeta)
    ev = cargar(carpeta)
    mmd = carpeta / "trayectoria.mmd"
    mmd.write_text(a_mermaid(ev) + "\n", encoding="utf-8")
    (carpeta / "metricas.json").write_text(json.dumps(metricas(ev), ensure_ascii=False, indent=1), encoding="utf-8")
    if png:
        renderizar_png(mmd)
    return ev


if __name__ == "__main__":
    carpetas = [pathlib.Path(c) for c in sys.argv[1:] if not c.startswith("--")] or \
        sorted(p for p in pathlib.Path("trazas").iterdir() if p.is_dir())
    for c in carpetas:
        generar(c, png="--png" in sys.argv)
        print(f"{c}: {json.dumps(metricas(cargar(c)), ensure_ascii=False)}")
