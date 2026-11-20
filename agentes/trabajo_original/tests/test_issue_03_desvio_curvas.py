"""Issue #3: el desvío se mide contra todos los tramos de la ruta (RF-04)."""
from rutasit.desvio import distancia_a_ruta, hay_desvio
from rutasit.gps import Posicion

# Ruta en "L" cerca del centro de Arequipa: ~2 km al este y luego ~2 km al norte.
A, B, C = (-16.4090, -71.5375), (-16.4090, -71.5188), (-16.3909, -71.5188)
TRAZADO = [A, B, C]


def test_issue_03_bus_en_la_esquina_no_esta_desviado():
    esquina = Posicion(B[0], B[1], 25.0)
    assert distancia_a_ruta(esquina, TRAZADO) < 1.0


def test_issue_03_bus_que_corta_la_curva_esta_desviado():
    # Dos posiciones por dentro de la "L", cerca de la recta A-C pero lejos de los dos tramos.
    dentro = [Posicion(-16.4018, -71.5300, 25.0), Posicion(-16.4009, -71.5291, 25.0)]
    assert hay_desvio(dentro, TRAZADO) is True


def test_issue_03_una_sola_posicion_fuera_no_es_desvio():
    sobre_ruta = Posicion(-16.4090, -71.5300, 25.0)
    fuera = Posicion(-16.4018, -71.5300, 25.0)
    assert hay_desvio([sobre_ruta, fuera], TRAZADO) is False
