"""B8_detecta_mutacion: si se cambia a proposito el comportamiento que el caso debe comprobar, las
pruebas generadas deben FALLAR. Asi se demuestra que prueban algo y no solo que pasan.
Cada mutacion es un cambio pequeno en una copia temporal de src (el repositorio no se toca)."""
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from comun import SRC, leer_pruebas, ejecutar_pytest

MUTACIONES = {
    "B1": ("eta.py", "max(pos.vel_kmh, 5.0)", "max(pos.vel_kmh, 1.0)"),
    "B2": ("eta.py", "if clave not in self._cache:", "if True:"),
    "B3": ("eta.py", "        except TimeoutError:\n            return self._respaldo", "        except Exception:\n            return self._respaldo"),
    "B4": ("eta.py", "tiempo_de_recorrido((pos.lat, pos.lon), paradero) / 60)", "tiempo_de_recorrido((pos.lat, pos.lon), paradero) / 30)"),
    "B5": ("eta.py", "for i in range(self._intentos):", "for i in range(self._intentos - 1):"),
    "B6": ("servicio.py", "if minutos > LIMITE_RETRASO_MIN:", "if minutos > LIMITE_RETRASO_MIN + 1000:"),
    "B7": ("estados.py", 'def verificar_eta(self, viaje): raise ValueError("El viaje aun no inicia")', "def verificar_eta(self, viaje): return None"),
    "B8": ("eta.py", "max(pos.vel_kmh, 5.0)", "max(pos.vel_kmh, 1.0)"),
}


def get_assert(output, context):
    codigo = leer_pruebas(output)
    if codigo is None:
        return {"pass": False, "score": 0, "reason": "No hay JSON con la clave 'pruebas'"}
    id_caso = context["vars"]["id"]
    archivo, viejo, nuevo = MUTACIONES[id_caso]
    ok_original, _ = ejecutar_pytest(codigo)
    if not ok_original:
        return {"pass": False, "score": 0, "reason": "No pasan con el codigo original; no se puede comparar"}
    with tempfile.TemporaryDirectory() as d:
        copia = pathlib.Path(d, "src")
        shutil.copytree(SRC, copia, ignore=shutil.ignore_patterns("__pycache__"))
        ruta = copia / "rutasit" / archivo
        texto = ruta.read_text(encoding="utf-8")
        if viejo not in texto:
            return {"pass": False, "score": 0, "reason": f"La mutacion no aplica a {archivo} (el codigo cambio)"}
        ruta.write_text(texto.replace(viejo, nuevo, 1), encoding="utf-8")
        pathlib.Path(d, "test_generado.py").write_text(codigo, encoding="utf-8")
        env = dict(os.environ, PYTHONPATH=str(copia), PYTHONDONTWRITEBYTECODE="1")
        try:
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", d],
                               cwd=d, env=env, capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            return {"pass": True, "score": 1, "reason": "La mutacion colgo las pruebas (detectada)"}
    detecta = r.returncode != 0
    return {"pass": detecta, "score": 1 if detecta else 0,
            "reason": "Las pruebas detectan la mutacion" if detecta else "Las pruebas siguen pasando con el comportamiento roto"}
