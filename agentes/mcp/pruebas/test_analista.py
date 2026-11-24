"""E4/E6: reproduce las corridas grabadas del analista en una copia del repositorio y revisa el resultado."""
import json, pathlib, re, shutil, subprocess, sys
import pytest

REPO = pathlib.Path(__file__).resolve().parents[3]
CORRIDAS = sorted(p.name for p in (REPO / "agentes" / "mcp" / "trayectorias").iterdir()
                  if p.is_dir() and re.fullmatch(r"analista_catalogo_v\d+", p.name))
VIGENTE = CORRIDAS[-1]      # la del catálogo actual; las anteriores son evidencia histórica (otro servidor)


@pytest.mark.parametrize("corrida", [c for c in CORRIDAS if c == VIGENTE])
def test_corrida_grabada_responde_y_reporta_con_aprobacion(tmp_path, corrida):
    copia = tmp_path / "repo"
    ign = shutil.ignore_patterns("trabajo", "trazas", "__pycache__", "node_modules", "reportes")
    for d in ("src", "agentes", "docs", "prompts/criterios"):
        shutil.copytree(REPO / d, copia / d, ignore=ign)
    r = subprocess.run([sys.executable, "analista_mcp.py", "--corrida", corrida], cwd=copia / "agentes" / "mcp",
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, r.stderr[-2000:]
    assert "llega en 3 min" in r.stdout
    traz = copia / "agentes" / "mcp" / "trazas" / corrida
    assert [f.name for f in (traz / "reportes").iterdir()] == ["DESVIO-01.md"]
    met = json.loads((traz / "metricas.json").read_text(encoding="utf-8"))
    assert met["errores"] == 1                            # el error de la ruta "7", que el agente corrigió
    eventos = [json.loads(l) for l in (traz / "agente.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [e.get("humano") for e in eventos if e.get("accion") == "reportar_desvio"] == ["s"]
