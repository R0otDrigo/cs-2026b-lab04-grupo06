# Matriz de decisión — RutaSIT Arequipa

## Alternativas
- **A. Monolito en capas:** una aplicación con capas de presentación, lógica de negocio y acceso a datos. Es simple de construir, pero las funciones comparten la misma capa de negocio.
- **B. Monolito modular:** un despliegue dividido en módulos de ingesta, seguimiento, ETA, alertas y rutas, con interfaces explícitas, PostgreSQL y Redis como caché de posiciones. Mantiene una operación sencilla y ordena el código.
- **C. Arquitectura orientada a eventos:** las posiciones se publican en un broker (por ejemplo, RabbitMQ o Kafka) y servicios separados las consumen para ETA y alertas. Favorece el escalado independiente, pero agrega infraestructura y carga operativa.

## Criterios y pesos
| Criterio                   | Peso | Justificación (driver relacionado)                                |
|----------------------------|-----:|-------------------------------------------------------------------|
| Rendimiento en tiempo real | 25 % | QA-01: ETA disponible en ≤ 15 s con una carga de 30 posiciones/s  |
| Tiempo de entrega          | 25 % | R-01: el MVP debe estar en producción en 1 mes                    |
| Modificabilidad            | 20 % | QA-03: agregar una regla de alerta requiere ≤ 2 días-persona      |
| Costo operativo            | 15 % | R-03: operación prevista en un solo VPS                           |
| Simplicidad operativa      | 15 % | R-02 y R-03: equipo de 3 developers y un solo VPS                 |
| **Total**                  | **100 %** |                                                               |

## Matriz de evaluación
Escala: 1 = muy malo; 2 = malo; 3 = aceptable; 4 = bueno; 5 = excelente.

| Criterio (peso)                  | A | B | C |
|----------------------------------|--:|--:|--:|
| Rendimiento en tiempo real (25 %) | 3 | 4 | 5 |
| Tiempo de entrega (25 %)          | 5 | 4 | 2 |
| Modificabilidad (20 %)            | 2 | 4 | 4 |
| Costo operativo (15 %)            | 5 | 5 | 2 |
| Simplicidad operativa (15 %)      | 5 | 4 | 2 |
| **Total ponderado**               | **3,90** | **4,15** | **3,15** |

Los totales se calculan como la suma de cada puntaje multiplicado por su peso:

- **A:** 0,25×3 + 0,25×5 + 0,20×2 + 0,15×5 + 0,15×5 = **3,90**.
- **B:** 0,25×4 + 0,25×4 + 0,20×4 + 0,15×5 + 0,15×4 = **4,15**.
- **C:** 0,25×5 + 0,25×2 + 0,20×4 + 0,15×2 + 0,15×2 = **3,15**.

## Conclusión
Elegimos el **monolito modular (B)** porque obtuvo el mayor puntaje (4,15), separa las funciones y permite mantener un solo despliegue. Esto se ajusta al plazo de R-01 y al VPS de R-03. La opción orientada a eventos rinde mejor en la matriz, pero requiere más operación para el equipo y el plazo disponibles. El monolito en capas quedó segundo (3,90), aunque su puntaje bajo en modificabilidad hace más difícil aislar cambios. La recomendación de esta revisión asistida por IA también es el monolito modular; coincide con la decisión del equipo porque ofrece el mejor balance entre rendimiento, plazo y operación. Ver [ADR-001](adr/001-estilo-arquitectonico.md).

## Nota sobre la IA
En esta revisión asistida por IA se afirmó que usar Redis bastaría para cumplir el tiempo del ETA. Esa afirmación es exagerada: Redis puede ayudar con las lecturas, pero no asegura por sí solo el resultado de QA-01. Lo verificamos al comparar la afirmación con QA-01 en `drivers.md`: el requisito pide procesar 30 posiciones por segundo y tener el ETA en ≤ 15 s (p95), pero no presenta resultados de una prueba. Por eso el rendimiento sigue siendo una meta por comprobar; hace falta ejecutar una prueba con 300 buses y 1 000 consultas.
