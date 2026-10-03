# Drivers arquitectónicos - RutaSIT Arequipa

## 1. Requisitos funcionales clave
| ID    | Requisito                                                      | Actor     | Prioridad |
|-------|----------------------------------------------------------------|-----------|-----------|
| RF-01 | Recibir la posición GPS (id de bus, latitud, longitud, hora)   | Bus       | Alta      |
| RF-02 | Mostrar la ubicación de los buses en el mapa                   | Pasajero  | Alta      |
| RF-03 | Calcular y mostrar el tiempo estimado de llegada (ETA)         | Pasajero  | Alta      |
| RF-04 | Generar alertas de desvío o congestión                         | Operador  | Media     |
| RF-05 | Administrar rutas, paraderos y buses                           | Operador  | Media     |
| RF-06 | Buscar un paradero y ver los próximos buses que llegan         | Pasajero  | Alta      |

## 2. Atributos de calidad (ordenados por prioridad)
1. Rendimiento en tiempo real — el ETA pierde valor si llega tarde; 300 buses reportan cada 10 s.
2. Disponibilidad — el pasajero consulta en horas de movilidad y un bus sin señal no debe romper el mapa.
3. Modificabilidad — se agregarán rutas, paraderos y reglas de alerta con frecuencia.
4. Capacidad de interacción — el pasajero consulta desde el celular, con datos móviles limitados.

## 3. Restricciones
| ID   | Tipo         | Restricción                                                                 |
|------|--------------|-----------------------------------------------------------------------------|
| R-01 | Plazo        | MVP en producción en 1 mes                                                  |
| R-02 | Equipo       | 3 developers con experiencia en Python/Django y JavaScript                  |
| R-03 | Presupuesto  | Bajo: un solo servidor en la nube (VPS); sin servicios de pago de mapas     |
| R-04 | Tecnología   | PWA web (sin app nativa); mapas con OpenStreetMap                           |
| R-05 | Normativa    | Ley 29733: el MVP no almacena datos personales de pasajeros                 |

## 4. Escenarios de atributos de calidad
| ID    | Atributo        | Fuente        | Estímulo                                   | Entorno                      | Artefacto               | Respuesta                                                                    | Medida                                          |
|-------|-----------------|---------------|--------------------------------------------|------------------------------|-------------------------|------------------------------------------------------------------------------|-------------------------------------------------|
| QA-01 | Rendimiento     | 300 buses     | Envían su posición cada 10 s (30 pos/s)    | Hora punta, 1 000 pasajeros consultando | Módulos de ingesta y ETA | Guarda la posición y recalcula el ETA de los paraderos afectados            | ETA disponible en ≤ 15 s tras recibir la posición (p95) |
| QA-02 | Disponibilidad  | Un bus        | Pierde señal GPS durante 60 s              | Operación normal             | Módulo de seguimiento   | Muestra la última posición marcada "sin señal" y el resto del mapa sigue normal | 0 errores 5xx; marca "sin señal" a los 30 s sin datos; disponibilidad ≥ 99 % en horario de operación |
| QA-03 | Modificabilidad | Operador      | Pide agregar una nueva regla de alerta     | Desarrollo                   | Módulo de alertas       | Se agrega la regla sin modificar los demás módulos                           | ≤ 2 días-persona; 0 archivos modificados fuera del módulo |
