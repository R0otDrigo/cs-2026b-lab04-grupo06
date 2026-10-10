# Round-trip — RutaSIT Arequipa

| # | Diferencia observada | Causa | Acción |
|---|----------------------|-------|--------|
| 1 | No aparecen la composición Viaje–Posicion ni la asociación Ruta–Paradero; figuran como atributos `list[...]`. | pyreverse no infiere asociaciones desde colecciones tipadas. | Ninguna: limitación de la herramienta. Se mantiene el diagrama de diseño. |
| 2 | No hay multiplicidades. | El código no las expresa. | Se agregó en `Ruta.__post_init__` la validación de 2 o más paraderos (regla C3). |
| 3 | `ProveedorMapas` y `RepositorioViajes` aparecen como clases abstractas sin «puerto», y `OsmAdapter` sale con flecha de herencia, no de realización. | Python implementa interfaces con ABC. | Aceptable en Python. Se documenta. |
| 4 | No se ven los signos de visibilidad (+/-) y varios atributos salen sin tipo (bus, estado, ruta, paradero). | pyreverse dibuja como relación los atributos cuyo tipo es otra clase y no muestra visibilidad. | Se documenta. El diagrama de diseño es el que manda. |
| 5 | `ServicioEta` aparece con agregación hacia los puertos y hacia `ServicioAlertas`; en el diseño era dependencia. | Los objetos se reciben en el constructor y se guardan como atributos. | Se mantiene la dependencia en el diseño y se deja constancia. |
| 6 | Nombres en snake_case (`esta_sin_senal`) frente a camelCase en el diagrama (`estaSinSenal`). | Convención de Python. | Aceptable. Se documenta la equivalencia (C5). |
