# Comparaciones — RutaSIT Arequipa

## 1. Secuencia UML frente a vista dinámica C4 (E4)

La secuencia UML del Lab 05 muestra el detalle de las clases: quién llama a quién (ServicioEta, RepositorioViajes, Viaje), los nombres exactos de las operaciones, el ciclo `loop` por cada viaje activo y las ramas `alt` de éxito y error. Eso sirve a los developers que van a escribir el código. La vista dinámica C4 cuenta el mismo flujo con solo 5 pasos entre módulos y contenedores (PWA, ETA, Seguimiento, mapas, Alertas y caché). No muestra los bucles ni las ramas de error. Sirve para explicar el recorrido al equipo técnico y a quien no necesita ver las clases. Los 5 pasos usan relaciones que ya existen en el modelo.

## 2. Escribir a mano frente a modelar y exportar (E6)

Se compara `contexto-manual.puml` (C4-PlantUML escrito a mano) con la vista de contexto exportada desde `workspace.dsl`.

| Aspecto | Escrito a mano | Modelo exportado |
|---------|----------------|------------------|
| Esfuerzo | 18 líneas para una sola vista | 139 líneas de DSL para el modelo completo, de las que salen las 5 vistas |
| Tiempo de generación | Hay que escribir cada vista | 4,5 segundos para exportar las 5 vistas en PlantUML y Mermaid |
| Errores o diferencias encontradas | Hay que escribir cada macro. Se usó `System_Ext` para los externos | El export de C4-PlantUML usó `System` también para los externos: se ven igual que RutaSIT. Se probó agregar la etiqueta `External` y no cambió nada. El export a Mermaid sí los muestra en gris |
| Si cambia el nombre de un elemento | Hay que corregirlo en cada archivo | Se cambia en una línea del DSL y se vuelve a exportar |

**Prueba del cambio de nombre.** Se cambió `softwareSystem "RutaSIT"` por `"RutaSIT Arequipa"` en una sola línea del DSL y se volvió a exportar: las 5 vistas se actualizaron solas (66 líneas distintas). El nombre aparece en 72 líneas de las 5 vistas; escritas a mano habría que revisar las 72 una por una, en 5 archivos.

**Conclusión.** Para una sola vista pequeña, escribirla a mano es rápido. En cuanto hay varias vistas que hablan de los mismos elementos, conviene el modelo único, porque todas cambian juntas y no se desordenan. La contra es que el export tiene límites de estilo (por ejemplo, los sistemas externos).
