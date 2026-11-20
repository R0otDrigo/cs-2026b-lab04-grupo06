"""E3 (Grupo 06): decisiones inválidas propias, política adaptada a RutaSIT y modo interactivo."""
import json, pathlib, sys
import pytest

AGENTES = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTES))
from agente.contrato import validar_decision            # noqa: E402
from agente.politica import Politica                     # noqa: E402
from agente.herramientas import Herramientas             # noqa: E402
from agente.modelos import ModeloGrabado, ModeloInteractivo     # noqa: E402
from agente.nucleo import Agente                         # noqa: E402

# ---------- E3: decisiones inválidas propias ----------
CONOCIDAS = {"leer_archivo", "editar_archivo", "ejecutar_pruebas", "mapa_repo"}


@pytest.mark.parametrize("decision, motivo", [
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": {"ruta": "a.py"}, "confianza": 0.9},
     "campos no permitidos"),                                                        # campo de más
    ({"pensamiento": "leo", "accion": "leer_archivo", "args": "ruta=src/rutasit/gps.py"},
     "'args' debe ser un objeto JSON"),                                              # args como texto
    ({"pensamiento": "leo", "accion": "", "args": {}}, "herramienta desconocida"),   # acción vacía
    ({"pensamiento": "   ", "accion": "leer_archivo", "args": {}}, "falta 'pensamiento'"),   # pensamiento vacío
    ({"pensamiento": "listo", "final": {"estado": "ok"}}, "'final' debe ser texto"), # final no es texto
    ('```json\n{"pensamiento": "x", "final": "y"}\n```', "debe ser un objeto JSON"), # JSON en bloque de código
    ({"pensamiento": "calculo", "accion": "ejecutar_python", "args": {"codigo": "1+1"}},
     "herramienta desconocida"),                                                     # herramienta inventada
])
def test_contrato_rechaza_decisiones_invalidas(decision, motivo):
    ok, texto = validar_decision(decision, CONOCIDAS)
    assert ok is False
    assert motivo in texto


def test_agente_devuelve_el_error_de_contrato_como_observacion(tmp_path):
    decisiones = [{"pensamiento": "x", "accion": "leer_archivo", "args": "a.py"},
                  {"pensamiento": "corrijo el formato", "final": "listo"}]
    (tmp_path / "d.json").write_text(json.dumps(decisiones), encoding="utf-8")
    ag = Agente("ejecutor", ModeloGrabado(tmp_path / "d.json"), Herramientas(tmp_path), Politica(),
                "objetivo", str(tmp_path / "t.jsonl"))
    assert ag.ejecutar() == "listo"
    estados = [json.loads(l)["estado"] for l in (tmp_path / "t.jsonl").read_text(encoding="utf-8").splitlines()]
    assert estados == ["INICIO", "CONTRATO_INVALIDO", "FINALIZADO"]
    assert "ERROR DE CONTRATO" in ag.historial[2]["content"]


def test_agente_se_detiene_al_agotar_el_presupuesto(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    decisiones = [{"pensamiento": "leo otra vez", "accion": "leer_archivo", "args": {"ruta": "a.py"}}] * 5
    (tmp_path / "d.json").write_text(json.dumps(decisiones), encoding="utf-8")
    ag = Agente("ejecutor", ModeloGrabado(tmp_path / "d.json"), Herramientas(tmp_path), Politica(max_pasos=2),
                "objetivo", str(tmp_path / "t.jsonl"))
    assert ag.ejecutar() == "(sin respuesta final)"
    assert ag.eventos[-1]["estado"] == "LIMITE_ALCANZADO"


# ---------- Política adaptada a RutaSIT ----------
@pytest.mark.parametrize("ruta", ["test/test_viaje.py", "tests/test_issue_01_gps_sin_datos.py",
                                  "./test/conftest.py", "test\\test_patrones.py"])
def test_politica_protege_las_dos_carpetas_de_pruebas(ruta):
    d = Politica().evaluar("editar_archivo", {"ruta": ruta, "antes": "a", "despues": "b"}, 1)
    assert not d.permitido and "Ruta protegida" in d.motivo


def test_politica_bloquea_python_c():
    d = Politica().evaluar("ejecutar_comando", {"comando": "python -c \"print(1)\""}, 1)
    assert not d.permitido


def test_interactivo_no_se_cae_si_lo_pegado_no_es_json(tmp_path):
    m = ModeloInteractivo(str(tmp_path / "t.json"), entrada=lambda _: "Claro, voy a leer el archivo gps.py")
    d = m.decidir([{"role": "user", "content": "objetivo"}])
    assert d == "Claro, voy a leer el archivo gps.py"
    assert validar_decision(d, CONOCIDAS)[0] is False
    assert json.loads((tmp_path / "t.json").read_text(encoding="utf-8")) == [d]
