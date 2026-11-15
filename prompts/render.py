"""Rellena una plantilla de prompt con una historia: python render.py <carpeta> <version> <id>.
Sirve para ver exactamente el texto que recibe el modelo."""
import pathlib
import sys

import yaml

carpeta, version, id_caso = sys.argv[1:4]
raiz = pathlib.Path(__file__).parent / carpeta
plantilla = (raiz / f"{version}.txt").read_text(encoding="utf-8")
casos = yaml.safe_load((raiz / "casos.yaml").read_text(encoding="utf-8"))
vars_ = next(c["vars"] for c in casos if c["vars"]["id"] == id_caso)
texto = plantilla
for clave, valor in vars_.items():
    texto = texto.replace("{{" + clave + "}}", str(valor))
sys.stdout.write(texto)
