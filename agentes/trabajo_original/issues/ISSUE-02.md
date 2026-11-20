# Issue #2: El tiempo de llegada sale negativo si el bus ya pasó el paradero

**Reportado por:** pasajeros (comentarios en la app)

**Observado:** con la estrategia `RECORRIDO`, un pasajero en el paradero del km 2,0 consulta cuando el
bus va en el km 3,0 a 30 km/h y la app muestra "llega en -2 min".

**Esperado:** si el bus ya pasó el paradero, no hay tiempo de llegada: el sistema responde
"ETA no disponible" (HU-01) en lugar de minutos negativos. Si el bus está justo en el paradero, son 0 minutos.

**Prueba que reproduce el error:**
`tests/test_issue_02_eta_paradero_pasado.py`
