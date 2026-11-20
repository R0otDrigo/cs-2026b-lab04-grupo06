"""E4 (Grupo 06): herramienta mapa_repo y memoria de notas."""
import pathlib, sys
import pytest

AGENTES = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AGENTES))
from agente.herramientas import Herramientas             # noqa: E402


# ---------- E4: mapa_repo y memoria de notas ----------
def _repo_pequeno(tmp_path):
    pkg = tmp_path / "src" / "demo"
    pkg.mkdir(parents=True)
    (pkg / "rutas.py").write_text(
        "class Ruta:\n    def __init__(self, codigo):\n        self.codigo = codigo\n"
        "    def largo_km(self, desde, hasta):\n        return 0\n\n"
        "def distancia(a, b):\n    return 0\n", encoding="utf-8")
    (pkg / "roto.py").write_text("def mal(:\n", encoding="utf-8")
    return Herramientas(tmp_path, extendidas=True)


def test_mapa_repo_lista_clases_metodos_y_funciones_con_linea(tmp_path):
    mapa = _repo_pequeno(tmp_path).mapa_repo("src")
    assert "src/demo/rutas.py" in mapa
    assert "class Ruta (l.1): largo_km(desde, hasta)" in mapa
    assert "def distancia(a, b) (l.7)" in mapa
    assert "roto.py: ERROR de sintaxis" in mapa


def test_mapa_repo_no_sale_del_sandbox(tmp_path):
    with pytest.raises(PermissionError):
        _repo_pequeno(tmp_path).mapa_repo("../..")


def test_notas_se_guardan_y_se_leen(tmp_path):
    h = Herramientas(tmp_path, extendidas=True)
    assert h.leer_notas() == "(sin notas)"
    assert h.anotar("Hipótesis: desvio.py usa solo inicio y fin") == "OK: nota 1"
    assert h.anotar("Revisado: src/rutasit/desvio.py") == "OK: nota 2"
    notas = h.leer_notas()
    assert "Hipótesis" in notas and "Revisado" in notas
    assert h.anotar("").startswith("ERROR") and h.anotar("x" * 301).startswith("ERROR")


def test_herramientas_extendidas_solo_si_se_activan(tmp_path):
    assert "mapa_repo" not in Herramientas(tmp_path).catalogo()
    assert {"mapa_repo", "anotar", "leer_notas"} <= set(Herramientas(tmp_path, extendidas=True).catalogo())
