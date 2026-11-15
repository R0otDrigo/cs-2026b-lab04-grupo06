import ast, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from comun import leer_pruebas

PROHIBIDOS = {"requests", "socket", "urllib", "http", "httpx", "subprocess"}


def get_assert(output, context):
    codigo = leer_pruebas(output)
    if codigo is None:
        return {"pass": False, "score": 0, "reason": "No hay JSON con la clave 'pruebas'"}
    try:
        arbol = ast.parse(codigo)
    except SyntaxError:
        return {"pass": False, "score": 0, "reason": "No compila"}
    malos = set()
    for n in ast.walk(arbol):
        if isinstance(n, ast.Import):
            malos |= {a.name.split(".")[0] for a in n.names} & PROHIBIDOS
        elif isinstance(n, ast.ImportFrom) and n.module:
            malos |= {n.module.split(".")[0]} & PROHIBIDOS
        elif isinstance(n, ast.Attribute) and n.attr in ("environ", "getenv"):
            malos.add(n.attr)
        elif isinstance(n, ast.Call) and getattr(n.func, "attr", getattr(n.func, "id", "")) == "sleep":
            malos.add("sleep")
    return {"pass": not malos, "score": 0 if malos else 1,
            "reason": "Sin red, claves ni esperas" if not malos else f"Usa: {sorted(malos)}"}
