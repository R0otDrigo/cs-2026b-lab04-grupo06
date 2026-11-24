"""E4: el agente del Lab 10 ve al servidor MCP como herramientas locales; la escritura exige aprobación."""
import pathlib, sys
from mcp import StdioServerParameters

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ.parent))                          # agentes/: framework del Lab 10
from agente.herramientas_mcp import HerramientasMCP          # noqa: E402
from agente.politica import Politica                          # noqa: E402


def test_adaptador_descubre_ejecuta_y_la_politica_exige_aprobacion(tmp_path):
    import os
    h = HerramientasMCP(StdioServerParameters(command=sys.executable,
                                              args=[str(RAIZ / "servidor_mcp" / "rutasit_mcp.py")],
                                              env={**os.environ, "RUTASIT_REPORTES": str(tmp_path)}))
    try:
        assert {"buses_en_ruta", "tiempo_llegada", "reportar_desvio", "leer_recurso"} <= set(h.catalogo())
        assert '"minutos": 3' in h.tiempo_llegada(ruta="R-07", paradero="Plaza de Armas")
        assert h.buses_en_ruta(ruta="7").startswith("ERROR")
        assert "Plaza de Armas" in h.leer_recurso(uri="rutasit://rutas")
        assert h.herramientas_de_escritura() == {"reportar_desvio"}
        p = Politica(herramientas_permitidas=set(h.catalogo()), requieren_aprobacion=h.herramientas_de_escritura())
        args = {"placa": "V2B-789", "descripcion": "x" * 30}
        assert not p.evaluar("reportar_desvio", args, 1).permitido                 # sin aprobador
        p.aprobar = lambda accion, a: False
        assert p.evaluar("reportar_desvio", args, 1).humano == "n"
        p.aprobar = lambda accion, a: True
        assert p.evaluar("reportar_desvio", args, 1).permitido
        assert p.evaluar("buses_en_ruta", {"ruta": "R-07"}, 1).humano is None      # la lectura no pregunta
    finally:
        h.cerrar()
