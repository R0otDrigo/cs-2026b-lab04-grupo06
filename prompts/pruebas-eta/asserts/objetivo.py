"""B7_prueba_el_objetivo: las pruebas generadas deben referirse a la clase o funcion pedida y al
comportamiento esperado del caso (no basta con que compilen y pasen)."""
import re
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from comun import leer_pruebas

# Palabras que deben aparecer en el codigo de las pruebas, por caso (todas, sin distinguir mayusculas).
REQUISITOS = {
    "B1": ["EtaPorVelocidad", "Posicion"],
    "B2": ["ConCacheEta"],
    "B3": ["ConRespaldo", "TimeoutError"],
    "B4": ["EtaPorMapas"],
    "B5": ["ConReintentosEta", "TimeoutError"],
    "B6": ["ServicioEta", "consultar_eta", "retraso", "eventos", "disponible"],
    "B7": ["verificar_eta", "PROGRAMADO", "FINALIZADO", "EN_RUTA", "ValueError"],
    "B8": ["EtaPorVelocidad", "Posicion"],
}


def get_assert(output, context):
    codigo = leer_pruebas(output)
    if codigo is None:
        return {"pass": False, "score": 0, "reason": "No hay JSON con la clave 'pruebas'"}
    faltan = [p for p in REQUISITOS.get(context["vars"]["id"], []) if not re.search(re.escape(p), codigo, re.I)]
    return {"pass": not faltan, "score": 0 if faltan else 1,
            "reason": "Prueba el objetivo" if not faltan else f"Las pruebas no mencionan: {faltan}"}
