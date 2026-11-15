# Encadenamiento Tarea A a Tarea B

La guia lo pide "si la tarea lo permite". En este caso no se encadenaron: la Tarea B genera pruebas pytest a partir del CODIGO de `rutasit` (clases de ETA, `ServicioEta`, estados), y la Tarea A produce criterios de aceptacion en lenguaje de negocio a partir de historias. Usar los escenarios de la Tarea A como entrada de la Tarea B habria obligado a inventar la traduccion entre "veo ETA no disponible" y llamadas a `ServicioEta`, y los errores de la Tarea A se habrian propagado a las pruebas.

Lo que si se hizo: la Tarea B recibe en el prompt el comportamiento esperado de cada caso (`esperado` de `pruebas-eta/casos.yaml`, v3.2), que cumple el papel de criterio de aceptacion, y los resultados del retraso mayor a 20 minutos coinciden con la regla aprobada que tambien usa v5 de la Tarea A.
