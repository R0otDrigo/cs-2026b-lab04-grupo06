import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from comun import ejecutar_pytest, leer_pruebas


def get_assert(output, context):
    codigo = leer_pruebas(output)
    if codigo is None:
        return {"pass": False, "score": 0, "reason": "No hay JSON con la clave 'pruebas'"}
    ok, resumen = ejecutar_pytest(codigo)
    return {"pass": ok, "score": 1 if ok else 0, "reason": f"pytest: {resumen}"}
