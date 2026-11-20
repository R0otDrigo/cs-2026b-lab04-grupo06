"""E6 (Grupo 06): humano en el circuito; solo acepta s o n."""
import json, pathlib, sys

AGENTES = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTES))
from agente.politica import Politica                     # noqa: E402
from agente.humano import AprobadorConsola, AprobadorGrabado   # noqa: E402


# ---------- E6: humano en el circuito ----------
def test_aprobar_edicion_se_puede_pasar_al_constructor():
    p = Politica(aprobar_edicion=lambda args: False)
    d = p.evaluar("editar_archivo", {"ruta": "src/rutasit/gps.py", "antes": "a", "despues": "b"}, 1)
    assert (d.permitido, d.humano) == (False, "n")


def test_consola_solo_acepta_s_o_n(tmp_path):
    respuestas, mensajes = iter(["x", "si", " S "]), []
    aprobador = AprobadorConsola(entrada=lambda _: next(respuestas), salida=mensajes.append,
                                 grabar_en=tmp_path / "humano.json")
    assert aprobador({"ruta": "src/rutasit/gps.py", "antes": "a", "despues": "b"}) is True
    assert sum("escriba solo 's' o 'n'" in m for m in mensajes) == 2
    assert json.loads((tmp_path / "humano.json").read_text(encoding="utf-8")) == ["s"]


def test_consola_rechazo_y_grabado_reproducen_lo_mismo(tmp_path):
    aprobador = AprobadorConsola(entrada=lambda _: "n", salida=lambda _: None, grabar_en=tmp_path / "h.json")
    assert aprobador({"ruta": "src/x.py", "antes": "a", "despues": "b"}) is False
    assert AprobadorGrabado(tmp_path / "h.json")({"ruta": "src/x.py"}) is False
