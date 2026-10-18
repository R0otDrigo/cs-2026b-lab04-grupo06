# Inventario de elementos — RutaSIT Arequipa

Tabla de todo lo que aparece en el modelo C4 y de qué archivo de los Laboratorios 04 y 05 sale.

| Elemento | Tipo C4 | Origen |
|----------|---------|--------|
| Pasajero | Persona | drivers.md (Lab 04) |
| Operador | Persona | drivers.md (Lab 04) |
| RutaSIT | Sistema de software | Caso (Lab 04) |
| Dispositivos GPS de los buses | Sistema externo | drivers.md (RF-01) y ADR-002 (Lab 04) |
| Proveedor de mapas | Sistema externo | ADR-001 y clases.puml: puerto ProveedorMapas y OsmAdapter (Lab 05) |
| Aplicación web progresiva | Contenedor | ADR-001 y despliegue.py (Lab 04) |
| API RutaSIT (monolito modular, Django) | Contenedor | ADR-001 y despliegue.py (Lab 04) |
| Base de datos (PostgreSQL + PostGIS) | Contenedor | ADR-001 y despliegue.py (Lab 04) |
| Caché (Redis) | Contenedor | ADR-003 y despliegue.py (Lab 04) |
| Módulos Ingesta, Seguimiento, ETA, Alertas y Rutas | Componente (de la API) | paquetes.puml (Lab 05) y ADR-001 |
| Nginx y Grafana | Nodo de infraestructura (solo en el despliegue) | despliegue.py (Lab 04) |
| Flujo "consultar la llegada del bus" | Vista dinámica | secuencia-consultar-eta.puml (Lab 05) |
| Clases del módulo (Viaje, Posicion, etc.) | Nivel 4 (código), no se dibuja de nuevo | clases.puml (Lab 05) |

## Notas

- El paquete **compartido** de paquetes.puml no aparece como componente: son utilidades que usan todos los módulos y no tienen responsabilidad propia.
- Nginx y Grafana no son contenedores C4: no son parte de lo que construimos, solo ayudan a que funcione. Por eso van como nodos de infraestructura en la vista de despliegue.
- Los GPS de los buses son un sistema externo: los fabrica y los instala otro, nosotros solo recibimos lo que envían (ADR-002).
