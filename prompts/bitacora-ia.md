# Bitácora de IA — Laboratorio 09 · RutaSIT Arequipa

Herramienta: Claude. Las respuestas para las evaluaciones (carpetas `grabaciones/`) las generaron subagentes de Claude con herramientas de archivo limitadas (ver `PROCEDENCIA.md`), con el prompt de cada version, y se guardaron sin editar. Es una limitacion: no es un chat normal ni el modelo de produccion.

| # | Herramienta | Que se pidio | Que propuso la IA | Que verificamos o corregimos | Decision |
|---|-------------|--------------|-------------------|------------------------------|----------|
| 1 | Claude | Redactar las asercion A5 (que el prompt resista una orden inyectada en H9). | Fallar si el texto contenia la palabra APROBADO. | Dio falso positivo: una respuesta correcta citaba la palabra al rechazar la orden. Se cambio a comparar que toda la salida sea esa palabra. | Corregida |
| 2 | Claude | Escribir las asercion S4 y S5 de red teaming en JavaScript. | Bloques `try`/`return` en una sola linea. | promptfoo dio SyntaxError. Se reescribieron en varias lineas y se volvio a correr el eval. | Corregida |
| 3 | Claude | Contar los asserts de las pruebas generadas (Tarea B, regla B3). | Contar solo la palabra `assert`. | Dejaba fuera `pytest.raises`, asi que una prueba valida salia con menos de 3. Se cuentan ambos y el informe guarda las dos cifras. | Corregida |
| 4 | Claude | Prompt v2 de la Tarea A. | Respuestas con mas de 4 escenarios y sin cumplir el esquema. | Fallo A1 en 9/9 casos. En v3 se fijo el maximo y se agrego un ejemplo. | Rechazada (v2) |
| 5 | Claude | Ejemplo few-shot de la Tarea B (v3). | Un ejemplo con solo 2 asserts. | Contradecia la regla de 3 asserts y el modelo copio el patron. Se corrigio el ejemplo. | Corregida |
| 6 | Claude | Caso B6 (el codigo bajo prueba usa el GPS). | Pruebas que suponian un estado inicial por defecto y una interfaz falsa del GPS inventada. | Fallaron al ejecutarse. En v3.1 se agregaron al CONTEXTO las interfaces reales del SDK. | Corregida |
| 7 | Claude | Atacar v1 con R3 (pedir el prompt). | — | La API bloqueo el pedido. No se rodeo; queda "sin dato" en `red-team.md`. | Registrado |
| 8 | Claude | Revisión externa (14/11/2026): ¿el evaluador de la Tarea B acepta pruebas que no prueban la función pedida? | Una prueba de relleno (`assert True` y dos más) con `funcion` inexistente pasaba todas las aserciones. | Se reprodujo: era un falso positivo real. Se agregaron `B7_prueba_el_objetivo` (menciona la clase y el comportamiento del caso) y `B8_detecta_mutacion` (si se rompe el código, las pruebas fallan). v3.1 bajó de 8/8 a 6/8 (B6 no comprueba el evento de retraso). | Corregida |
| 9 | Claude | La corrección de la entrada 3 (sumar `pytest.raises`) cumple la consigna? | Sumarlos y declarar 6 comprobaciones en B7 v3.1. | La guía pide 3 o más `assert`; B7 v3.1 tiene 2 `assert` y 4 `pytest.raises`. Se volvió a la regla literal, se informan los `pytest.raises` aparte y se creó v3.2 (pide 3 `assert` literales). Los resultados anteriores NO se editaron. | Rechazada (mi corrección anterior) |
| 10 | Claude | Aserción A6 del caso H4 (umbral de 150 m). | Exigir que toda cifra en metros fuera 150. | Era un falso negativo: 200 m es una distancia válida de un bus ya desviado. v5 pasó a 9/9 solo después de corregir la aserción; se anotó aquí y en el código. v3 y v4 se reevaluaron con la regla corregida y siguen fallando H4 (no tienen la regla de 150 m). | Corregida |
| 11 | Claude | Caso H5: «una ruta no puede quedar con menos de 2 paraderos». | Dejarlo como esperado de «agregar un paradero». | No aplica: agregar nunca reduce paraderos. Se cambió el esperado a «paradero repetido o datos incompletos» y se anotó en el dataset. | Corregida |

> No se incluyó información personal ni confidencial en ningún prompt.
