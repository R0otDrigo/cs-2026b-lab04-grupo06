"""Proveedor de promptfoo que NO llama a ningun modelo: devuelve la respuesta grabada.

Cada respuesta esta en <carpeta>/grabaciones/<version>/<id>.txt y se guardo tal como la
dio el modelo (sin editarla). La version sale de la etiqueta del prompt (v1, v2, ...)
y el id del caso, de las variables del test. Para usar un modelo real basta cambiar
este proveedor por uno de promptfoo (por ejemplo anthropic:messages:...) en el yaml.
"""
import pathlib
import re

RAIZ = pathlib.Path(__file__).parent


def call_api(prompt, options, context):
    carpeta = options.get("config", {}).get("carpeta")
    # promptfoo pone en la etiqueta "<ruta>/vN.txt: <texto>": de ahi sale la version
    version = re.search(r"(v\d+(?:\.\d+)*)\.txt", context["prompt"]["label"]).group(1)
    id_caso = context["vars"]["id"]
    ruta = RAIZ / carpeta / "grabaciones" / version / f"{id_caso}.txt"
    if not ruta.exists():
        return {"error": f"Falta la grabacion {ruta.relative_to(RAIZ)}"}
    return {"output": ruta.read_text(encoding="utf-8")}
