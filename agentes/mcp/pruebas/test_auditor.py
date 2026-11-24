"""E7: las dos reglas nuevas del auditor y la auditoría del servidor propio y del de terceros."""
import asyncio, pathlib, sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "cliente"))
from auditar import auditar, revisar                     # noqa: E402

ESCRITURA = {"readOnlyHint": False, "destructiveHint": False}


def herramienta(annotations=None, **props):
    return {"name": "h", "description": "Herramienta de prueba con una descripción suficiente.",
            "inputSchema": {"type": "object", "properties": props}, "annotations": annotations}


def motivos(t):
    return [h[2] for h in revisar([t])]


def test_regla_nueva_escritura_sin_destructive_hint():
    assert "escritura sin destructiveHint explícito" in motivos(herramienta({"readOnlyHint": False}))
    assert "escritura sin destructiveHint explícito" not in motivos(herramienta(ESCRITURA))
    assert "escritura sin destructiveHint explícito" not in motivos(herramienta({"readOnlyHint": True}))


def test_regla_nueva_texto_libre_sin_max_length():
    t = herramienta(ESCRITURA, descripcion={"type": "string"}, placa={"type": "string", "maxLength": 7},
                    estado={"type": "string", "enum": ["A", "B"]}, dias={"type": "integer"})
    assert motivos(t) == ["parámetro de texto 'descripcion' sin maxLength"]


def test_servidor_propio_sin_hallazgos_y_terceros_con_alta(capsys):
    assert asyncio.run(auditar(str(RAIZ / "servidor_mcp" / "rutasit_mcp.py"))) is False
    assert "sin hallazgos" in capsys.readouterr().out
    assert asyncio.run(auditar(str(RAIZ / "terceros" / "clima_mcp.py"))) is True
    salida = capsys.readouterr().out
    assert "instrucciones ocultas" in salida and "'contexto' sin maxLength" in salida
