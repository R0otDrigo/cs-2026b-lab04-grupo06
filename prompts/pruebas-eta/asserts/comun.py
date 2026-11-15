"""Funciones comunes de las aserciones de la Tarea B (pruebas pytest para el ETA)."""
import ast
import json
import os
import pathlib
import subprocess
import sys
import tempfile

SRC = pathlib.Path(__file__).resolve().parents[3] / "src"


def leer_pruebas(output):
    """Devuelve el codigo de la clave 'pruebas', o None si la salida no cumple el contrato."""
    try:
        return json.loads(output)["pruebas"]
    except (ValueError, KeyError, TypeError):
        return None


def contar_asserts_literal(codigo):
    """Solo sentencias 'assert' (regla original de la guia)."""
    arbol = ast.parse(codigo)
    return sum(isinstance(n, ast.Assert) for n in ast.walk(arbol))


def contar_asserts(codigo):
    """Sentencias 'assert' + bloques 'with pytest.raises(...)'.

    Version corregida: la primera version solo contaba 'assert' y marco como fallo unas pruebas
    correctas de v3.1 (B7) que verifican el error con pytest.raises, que tambien es una comprobacion.
    """
    arbol = ast.parse(codigo)
    n = 0
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Assert):
            n += 1
        elif isinstance(nodo, ast.With):
            for item in nodo.items:
                f = getattr(item.context_expr, "func", None)
                if getattr(f, "attr", "") in ("raises", "warns") and getattr(getattr(f, "value", None), "id", "") == "pytest":
                    n += 1
    return n


def ejecutar_pytest(codigo):
    """Ejecuta las pruebas generadas contra el codigo REAL de src/rutasit, en un
    directorio temporal y con tiempo maximo de 60 s. Devuelve (ok, resumen)."""
    with tempfile.TemporaryDirectory() as d:
        pathlib.Path(d, "test_generado.py").write_text(codigo, encoding="utf-8")
        env = dict(os.environ, PYTHONPATH=str(SRC), PYTHONDONTWRITEBYTECODE="1")
        try:
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", d],
                               cwd=d, env=env, capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            return False, "tiempo agotado"
        ultima = (r.stdout.strip().splitlines() or ["sin salida"])[-1]
        return r.returncode == 0, ultima
