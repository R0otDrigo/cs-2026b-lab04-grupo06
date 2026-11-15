import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from comun import contar_asserts, contar_asserts_literal, leer_pruebas


def get_assert(output, context):
    """Regla literal de la guia: 3 o mas sentencias 'assert'. Los bloques pytest.raises se informan
    aparte, pero NO se suman (la version anterior de este evaluador los sumaba)."""
    codigo = leer_pruebas(output)
    if codigo is None:
        return {"pass": False, "score": 0, "reason": "No hay JSON con la clave 'pruebas'"}
    try:
        literal = contar_asserts_literal(codigo)
        total = contar_asserts(codigo)
    except SyntaxError:
        return {"pass": False, "score": 0, "reason": "No compila, no se pueden contar"}
    ok = literal >= 3
    return {"pass": ok, "score": 1 if ok else 0,
            "reason": f"{literal} assert literales ({total - literal} bloques pytest.raises aparte)"}
