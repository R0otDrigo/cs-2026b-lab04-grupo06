import re
from pathlib import Path

carpeta = Path(__file__).parent / "export"
texto = r'"((?:[^"\\]|\\.)*)"'

def args(linea):
    return re.findall(texto, linea)

def valor(linea, clave):
    m = re.search(r"\$" + clave + r'="((?:[^"\\]|\\.)*)"', linea)
    return m.group(1) if m else ""

total = {"vistas": 0, "elementos": 0, "relaciones": 0}
hallazgos = []
for f in sorted(carpeta.glob("*.puml")):
    src = f.read_text(encoding="utf-8")
    total["vistas"] += 1
    nombre = f.stem.replace("structurizr-", "")
    if not re.search(r"^title ", src, re.M):
        hallazgos.append((nombre, "General", "no tiene título"))
    if "SHOW_LEGEND" not in src:
        hallazgos.append((nombre, "General", "no tiene leyenda"))
    for linea in (l.strip() for l in src.splitlines()):
        m = re.match(r"(Person|System|System_Ext|Container|ContainerDb|ContainerQueue|Component|ComponentDb)\(", linea)
        if m:
            total["elementos"] += 1
            a = args(linea)
            if not a or not a[0].strip():
                hallazgos.append((nombre, "Elementos", f"elemento sin nombre: {linea[:50]}"))
            if not valor(linea, "descr"):
                hallazgos.append((nombre, "Elementos", f"{a[0] if a else '?'} no tiene descripción"))
            if m.group(1).startswith(("Container", "Component")) and not valor(linea, "techn"):
                hallazgos.append((nombre, "Elementos", f"{a[0]} no tiene tecnología"))
        if linea.startswith("Rel("):
            total["relaciones"] += 1
            a = args(linea)
            etiqueta = a[0] if a else ""
            if not etiqueta.strip():
                hallazgos.append((nombre, "Relaciones", "flecha sin etiqueta"))
            if not valor(linea, "techn"):
                hallazgos.append((nombre, "Relaciones", f'"{etiqueta}" no indica tecnología ni protocolo'))

print(f"Vistas: {total['vistas']} | elementos revisados: {total['elementos']} | relaciones revisadas: {total['relaciones']}")
print(f"Hallazgos: {len(hallazgos)}\n")
for v, g, d in hallazgos:
    print(f"[{v}] {g}: {d}")
