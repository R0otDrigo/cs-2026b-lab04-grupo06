"""Revisa las reglas C1, C2, C4 y C5 sobre los diagramas del Lab 05."""
import re, sys
from pathlib import Path

d = Path(__file__).parent
clases = (d / "clases.puml").read_text(encoding="utf-8")
sec = (d / "secuencia-consultar-eta.puml").read_text(encoding="utf-8")
est = (d / "estados-viaje.mmd").read_text(encoding="utf-8")
paq = (d / "paquetes.puml").read_text(encoding="utf-8")
codigo = "\n".join(p.read_text(encoding="utf-8") for p in (d.parent.parent / "src/rutasit").glob("*.py"))

# operaciones por clase/interfaz del diagrama de clases
ops = {}
for m in re.finditer(r"(?:class|interface)\s+(\w+)[^{\n]*\{(.*?)\n\}", clases, re.S):
    ops[m.group(1)] = set(re.findall(r"[+\-]\s*(\w+)\(", m.group(2)))

hallazgos = []

# C1: mensajes de la secuencia hacia objetos del dominio
alias = {"S": "ServicioEta", "R": "RepositorioViajes", "V": "Viaje",
         "G": "ProveedorMapas", "A": "ServicioAlertas"}
for m in re.finditer(r"^\s*(\w+)\s*-+>>?\s*(\w+)\s*:\s*(\w+)\(", sec, re.M):
    destino, op = m.group(2), m.group(3)
    if destino in alias and op not in ops[alias[destino]]:
        hallazgos.append(("C1", f"{alias[destino]}.{op}()", "no existe en el diagrama de clases"))
    if destino in alias: print(f"C1 ok  {alias[destino]}.{op}()") if op in ops[alias[destino]] else None

# C2: transiciones del diagrama de estados
for m in re.finditer(r"-->\s*\w+\s*:\s*(\w+)\(", est):
    op = m.group(1)
    if op not in ops["Viaje"]:
        hallazgos.append(("C2", f"Viaje.{op}()", "transición sin operación en la clase"))
    else:
        print(f"C2 ok  Viaje.{op}()")

# C4: ciclos entre paquetes
grafo = {}
for m in re.finditer(r"^(\w+)\s*\.\.>\s*(\w+)", paq, re.M):
    grafo.setdefault(m.group(1), set()).add(m.group(2))
def ciclo(n, ruta):
    for s in grafo.get(n, ()):
        if s in ruta: return ruta[ruta.index(s):] + [s]
        c = ciclo(s, ruta + [s])
        if c: return c
for n in list(grafo):
    c = ciclo(n, [n])
    if c: hallazgos.append(("C4", " -> ".join(c), "dependencia cíclica")); break
else:
    print("C4 ok  sin ciclos entre paquetes")

# C5: nombres del diagrama vs código (camelCase vs snake_case)
def snake(s): return re.sub(r"(?<!^)(?=[A-Z])", "_", s).lower()
for clase, nombres in ops.items():
    for op in sorted(nombres):
        if op != snake(op) and f"def {snake(op)}(" not in codigo:
            hallazgos.append(("C5", f"{clase}.{op}()", "no está en el código ni en snake_case"))
        elif op != snake(op):
            hallazgos.append(("C5", f"{clase}.{op}()", f"en el código es {snake(op)}() (equivalencia por convención de Python)"))

print()
for h in hallazgos: print(" | ".join(h))
sys.exit(0)
