"""Procedencia de plantillas y grabaciones.

  python3 prompts/procedencia.py generar    -> escribe prompts/procedencia.json
  python3 prompts/procedencia.py verificar  -> falla si una plantilla o grabacion cambio sin re-registrar

Guarda el hash (sha256) de cada plantilla de prompt y de cada grabacion. Si alguien cambia vN.txt, las grabaciones
de esa version ya no corresponden al prompt: la verificacion falla hasta volver a grabar (o declarar el cambio)."""
import hashlib
import json
import pathlib
import sys

RAIZ = pathlib.Path(__file__).parent
CARPETAS = {"criterios": RAIZ / "criterios", "pruebas-eta": RAIZ / "pruebas-eta", "seguridad": RAIZ / "seguridad"}


def sha(ruta):
    return hashlib.sha256(ruta.read_bytes()).hexdigest()[:16]


def calcular():
    datos = {}
    for nombre, carpeta in CARPETAS.items():
        # seguridad usa las plantillas de criterios
        plantillas = {p.stem: sha(p) for p in sorted((RAIZ / ("criterios" if nombre == "seguridad" else nombre)).glob("v*.txt"))}
        grabaciones = {str(g.relative_to(RAIZ)): sha(g) for g in sorted((carpeta / "grabaciones").rglob("*.txt"))}
        datos[nombre] = {"plantillas": plantillas, "grabaciones": grabaciones}
    return datos


if __name__ == "__main__":
    ruta = RAIZ / "procedencia.json"
    if sys.argv[1] == "generar":
        ruta.write_text(json.dumps(calcular(), indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    else:
        guardado = json.loads(ruta.read_text(encoding="utf-8"))
        actual = calcular()
        cambios = [f"{n}/{k}/{x}" for n in actual for k in actual[n] for x in actual[n][k]
                   if guardado.get(n, {}).get(k, {}).get(x) != actual[n][k][x]]
        cambios += [f"{n}/{k}/{x} (borrado)" for n in guardado for k in guardado[n] for x in guardado[n][k]
                    if x not in actual.get(n, {}).get(k, {})]
        if cambios:
            sys.exit("Cambiaron sin registrar:\n  " + "\n  ".join(cambios))
        print("procedencia ok")
