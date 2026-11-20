"""Issue #2: el ETA no puede ser negativo cuando el bus ya pasó el paradero."""
from rutasit.llegada import minutos_hasta_paradero


def test_issue_02_bus_antes_del_paradero():
    assert minutos_hasta_paradero(km_bus=1.0, km_paradero=2.0, vel_kmh=30) == 2


def test_issue_02_bus_en_el_paradero():
    assert minutos_hasta_paradero(km_bus=2.0, km_paradero=2.0, vel_kmh=30) == 0


def test_issue_02_bus_ya_paso_el_paradero():
    assert minutos_hasta_paradero(km_bus=3.0, km_paradero=2.0, vel_kmh=30) is None
