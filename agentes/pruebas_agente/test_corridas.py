"""Reproduce cada corrida grabada en trayectorias/ y comprueba que resuelve su issue sin tocar pruebas.
Las corridas se descubren solas: cada integrante que agrega una trayectoria agrega su caso de prueba."""
import pathlib, re, shutil, subprocess, sys
import pytest

AGENTES = pathlib.Path(__file__).resolve().parents[1]
CORRIDAS = sorted(p.name for p in (AGENTES / "trayectorias").iterdir() if p.is_dir())


def argumentos(corrida):
    m = re.fullmatch(r"issue(\d)_(unico|coordinado|interactivo)(_mapa)?(_humano)?", corrida)
    assert m, f"nombre de corrida no reconocido: {corrida}"
    args = ["--issue", m[1], "--modo", "unico" if m[2] == "interactivo" else m[2],
            "--corrida", corrida]
    if m[3]:
        args += ["--herramientas", "extendidas"]
    if m[4]:
        args += ["--humano", "grabado"]
    return args


@pytest.mark.parametrize("corrida", CORRIDAS)
def test_trayectoria_grabada_resuelve_el_issue(tmp_path, corrida):
    copia = tmp_path / "agentes"
    shutil.copytree(AGENTES, copia, ignore=shutil.ignore_patterns("trabajo", "trazas", "__pycache__"))
    r = subprocess.run([sys.executable, "orquestador.py", *argumentos(corrida)], cwd=copia,
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-2000:]
    trabajo = copia / "trabajo"
    prueba = next(trabajo.glob(f"tests/test_issue_0{corrida[5]}_*.py"))
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(prueba)],
                       cwd=trabajo, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout[-1500:]
    diff = (copia / "trazas" / corrida / "cambios.diff").read_text(encoding="utf-8")
    assert "+++ b/test" not in diff                      # ninguna corrida modificó pruebas
