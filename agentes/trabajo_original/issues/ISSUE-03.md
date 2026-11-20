# Issue #3: No se detecta el desvío cuando la ruta tiene una curva

**Reportado por:** centro de control del SIT

**Observado:** en una ruta en forma de "L" (2 km al este y luego 2 km al norte), un bus que corta camino
por dentro de la curva, a unos 800 m del trazado, no genera alerta de desvío. Al revés, un bus que pasa
por la esquina de la "L", sobre la ruta, aparece como desviado.

**Esperado:** se cumple RF-04: el bus está desviado solo si está a más de 150 m del trazado completo de
la ruta (todos sus tramos) en dos posiciones seguidas.

**Prueba que reproduce el error:**
`tests/test_issue_03_desvio_curvas.py`
