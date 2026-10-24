"""Calculo equivalente a `radon cc` y `radon raw` (para verificar sin instalar radon).
Reglas McCabe como radon: +1 por if/elif, for, while, except, assert, cada comprension,
cada operador booleano extra (and/or) y 'else' de bucles."""
import ast, io, sys, tokenize, glob, os


def cc(fn):
    n = 1
    for x in ast.walk(fn):
        if isinstance(x, (ast.If, ast.IfExp, ast.For, ast.While, ast.ExceptHandler, ast.Assert)):
            n += 1
        elif isinstance(x, ast.BoolOp):
            n += len(x.values) - 1
        elif isinstance(x, ast.comprehension):
            n += 1 + len(x.ifs)
        if isinstance(x, (ast.For, ast.While)) and x.orelse:
            n += 1
    return n


def rank(n):
    return "A" if n <= 5 else "B" if n <= 10 else "C" if n <= 20 else "D"


def metodos(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for f in node.body:
                if isinstance(f, ast.FunctionDef):
                    out.append((f"{node.name}.{f.name}", cc(f)))
        elif isinstance(node, ast.FunctionDef) and node not in [m for c in ast.walk(tree) if isinstance(c, ast.ClassDef) for m in c.body]:
            out.append((node.name, cc(node)))
    return out


def sloc(path):
    src = open(path, encoding="utf-8").read()
    lineas = set()
    doc = set()
    tree = ast.parse(src)
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef)) and n.body and isinstance(n.body[0], ast.Expr) \
                and isinstance(getattr(n.body[0], "value", None), ast.Constant) and isinstance(n.body[0].value.value, str):
            doc.update(range(n.body[0].lineno, n.body[0].end_lineno + 1))
    for tok in tokenize.generate_tokens(io.StringIO(src).readline):
        if tok.type in (tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER):
            continue
        for l in range(tok.start[0], tok.end[0] + 1):
            if l not in doc:
                lineas.add(l)
    return len(lineas)


def reporte(archivos, titulo):
    print(f"## {titulo}")
    todos, total = [], 0
    for a in archivos:
        total += sloc(a)
        for nombre, c in metodos(a):
            if nombre.split(".")[-1] != "__init__" or c > 1:
                todos.append((os.path.basename(a), nombre, c))
    for a, n, c in sorted(todos, key=lambda t: -t[2]):
        print(f"  {a:14s} {n:42s} {rank(c)} ({c})")
    prom = sum(c for _, _, c in todos) / len(todos)
    print(f"  metodos medidos: {len(todos)} | complejidad maxima: {max(c for *_, c in todos)} | promedio: {prom:.2f} ({rank(round(prom))}) | SLOC: {total} | archivos: {len(archivos)}")


if __name__ == "__main__":
    base = sys.argv[1]
    reporte([f"{base}/antes/servicio.py"], "ANTES")
    despues = [f for f in sorted(glob.glob(f"{base}/*.py")) if os.path.basename(f) not in ("__init__.py", "externos.py")]
    reporte(despues, "DESPUES")
