# Issue #1: El servicio de ETA se cae cuando el GPS del operador A no envía datos

**Reportado por:** operador de la empresa de transportes (turno mañana)

**Observado:** cuando el GPS de un bus del operador A pierde señal, el SDK responde `None` o un JSON
incompleto (sin `vel_kmh`). `AdaptadorGpsA.leer()` lanza `TypeError` o `KeyError` y la consulta de ETA
del pasajero termina en error 500.

**Esperado:** el adaptador devuelve `None` (sin posición). El servicio publica el evento `sin_senal`
para el operador y responde "ETA no disponible" (`Estimacion(0, False)`), igual que con el operador B.

**Prueba que reproduce el error:**
`tests/test_issue_01_gps_sin_datos.py`
