# E7: no determinismo (3 ejecuciones del prompt v4 sobre H1, H7 y H9)

Resultados completos en `comparacion.txt`; se regenera con `python3 prompts/no-determinismo/comparar.py > prompts/no-determinismo/comparacion.txt`.

**Alcance:** se midio con v4, que era la mejor version cuando se hizo. Despues se creo v5 (agrega las reglas aprobadas del proyecto) y no se repitieron las 3 ejecuciones con v5; el analisis es sobre la misma familia de prompt, no sobre v5.

- **Lo que se mantuvo igual en las 3 ejecuciones:** el veredicto INVEST (H1 y H9 siempre `true`, H7 siempre `false` con 0 escenarios), el JSON valido y la cantidad de escenarios (4 en H1 y H9).
- **Lo que cambio:** los textos. Ninguna ejecucion fue igual a otra byte a byte; la similitud de texto fue de 0,15 a 0,38. Los titulos de los escenarios cambian (por ejemplo, el cuarto escenario de H1 fue "Ningun bus en camino", "Bus proximo a llegar" y "Ruta sin buses en servicio"), y el numero de preguntas varia entre 2 y 3.
- **La mezcla de tipos tambien cambio una vez:** en H9 la ejecucion 3 dio `exito, exito, borde, borde` y las otras dos `exito, borde, borde, error`. Las dos cumplen el contrato, pero la segunda tiene un escenario de error y la primera no.
- **Que implica para las pruebas:** no se puede comparar el texto exacto. Las aserciones solo revisan propiedades (JSON valido, campos, cantidad y tipos minimos, que no aparezca implementacion, que se rechace una historia no INVEST). Aun asi, el caso de H9 muestra que una propiedad como "al menos un escenario de error" podria pasar o fallar segun la ejecucion; si la queremos exigir, hay que medir la tasa en varias ejecuciones y no en una sola.
- **Que implica para las grabaciones:** una grabacion es una sola muestra. Sirve para que la CI sea repetible, pero no prueba que el modelo real responda igual manana. Antes de confiar en una version hay que re-grabar con el modelo real, y la evaluacion con modelo real necesita temperatura baja y varias repeticiones.
