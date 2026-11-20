"""Humano en el circuito (Koenigstein, 2026, cap. 2): aprobar o rechazar cada edición.

AprobadorConsola pregunta en la terminal y valida la entrada: solo acepta "s" o "n".
Cada respuesta se graba para que la corrida se pueda reproducir con AprobadorGrabado.
"""
import json
import pathlib


def _resumen_edicion(args: dict) -> str:
    antes = str(args.get("antes", "")).strip().splitlines()
    despues = str(args.get("despues", "")).strip().splitlines()
    lineas = [f"Archivo: {args.get('ruta')}", "--- antes"]
    lineas += [f"  - {l}" for l in antes[:12]]
    lineas += ["+++ después"] + [f"  + {l}" for l in despues[:12]]
    return "\n".join(lineas)


class AprobadorConsola:
    def __init__(self, entrada=input, salida=print, grabar_en=None):
        self._entrada, self._salida = entrada, salida
        self._archivo = pathlib.Path(grabar_en) if grabar_en else None
        self.respuestas = []

    def __call__(self, args: dict) -> bool:
        self._salida("\n===== EL AGENTE QUIERE EDITAR UN ARCHIVO =====")
        self._salida(_resumen_edicion(args))
        while True:
            r = str(self._entrada("¿Aprueba la edición? [s/n]: ")).strip().lower()
            if r in ("s", "n"):
                break
            self._salida("Respuesta no válida: escriba solo 's' o 'n'.")
        self.respuestas.append(r)
        if self._archivo:
            self._archivo.parent.mkdir(parents=True, exist_ok=True)
            self._archivo.write_text(json.dumps(self.respuestas), encoding="utf-8")
        return r == "s"


class AprobadorGrabado:
    """Reproduce las respuestas que dio una persona en una corrida anterior."""

    def __init__(self, archivo):
        self._respuestas = json.loads(pathlib.Path(archivo).read_text(encoding="utf-8"))
        self._i = 0

    def __call__(self, args: dict) -> bool:
        r = self._respuestas[self._i]
        self._i += 1
        return r == "s"
