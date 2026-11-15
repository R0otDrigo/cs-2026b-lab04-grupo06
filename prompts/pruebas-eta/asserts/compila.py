import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from comun import leer_pruebas


def get_assert(output, context):
    codigo = leer_pruebas(output)
    if codigo is None:
        return {"pass": False, "score": 0, "reason": "No hay JSON con la clave 'pruebas'"}
    try:
        compile(codigo, "test_generado.py", "exec")
    except SyntaxError as e:
        return {"pass": False, "score": 0, "reason": f"No compila: {e}"}
    return {"pass": True, "score": 1, "reason": "Compila"}
