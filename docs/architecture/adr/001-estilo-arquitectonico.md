# ADR-001: Adoptar un monolito modular para el MVP de RutaSIT

- Estado: Aceptado
- Fecha: 2026-10-03
- Decisores: Estefanero Palma Rodrigo, Riveros Vilca Alberth Edwar y Sullca Mamani Mauro Snayder

## Contexto
El MVP debe estar en producción en 1 mes (R-01), con un equipo de 3 developers con experiencia en Python/Django y JavaScript (R-02), y operar en un solo VPS (R-03). El sistema debe recibir las posiciones GPS de los buses (RF-01); el escenario crítico exige 300 buses que reportan cada 10 s y que el ETA esté disponible en ≤ 15 s tras recibir una posición (QA-01). También se prevé agregar reglas de alerta sin modificar archivos fuera del módulo de alertas y en ≤ 2 días-persona (QA-03).

## Alternativas consideradas
1. **Monolito en capas (3,90):** simple de construir, pero sus funciones comparten la capa de negocio; obtuvo 2/5 en modificabilidad.
2. **Arquitectura orientada a eventos (3,15):** favorece el rendimiento, pero agrega infraestructura y carga operativa que no se ajustan al plazo, equipo y VPS (R-01, R-02, R-03).
3. **Monolito modular (4,15):** mantiene un despliegue y separa responsabilidades mediante módulos con interfaces explícitas; obtuvo el mayor total en la matriz.

## Decisión
Usaremos un monolito modular en Django con 5 módulos: Ingesta, Seguimiento, ETA, Alertas y Rutas. Los módulos se comunicarán mediante interfaces públicas y cada módulo tendrá su propio esquema en PostgreSQL. Las integraciones externas se implementarán mediante adaptadores.

## Consecuencias
- **Positivas:** un solo despliegue reduce la complejidad operativa (R-03); los módulos permiten agregar reglas de alerta con un límite verificable de ≤ 2 días-persona y 0 archivos modificados fuera del módulo (QA-03); es posible extraer módulos a servicios si las necesidades de carga cambian.
- **Negativas y riesgos:** el equipo debe respetar los límites entre módulos; se propone verificar dependencias con import-linter en CI. Una falla grave del proceso puede afectar a todo el sistema, porque los módulos comparten un despliegue.