# ADR-003: Actualizar el mapa del pasajero con polling cada 10 s sobre una caché en Redis

- Estado: Aceptado
- Fecha: 2026-10-02
- Decisores: Estefanero Palma Rodrigo, Sullca Mamani Mauro Snayder, Riveros Vilca Alberth Edwar
- Drivers relacionados: RF-02, RF-03, RF-06, QA-01, QA-02, R-01, R-02, R-04

## Contexto
RF-02 y RF-03 requieren mostrar las posiciones de los buses en el mapa y su tiempo estimado de llegada. QA-01 fija el atributo crítico: el ETA debe estar disponible en ≤ 15 s (p95) tras recibir la posición. QA-02 exige que un bus sin señal no rompa el mapa.

Los pasajeros consultan desde el celular y con datos móviles limitados, y el MVP es una PWA web, no una app nativa (R-04). El equipo son 3 developers de Django, sin experiencia declarada en async (R-02), con 1 mes de plazo (R-01).

Este ADR decide **cómo se propaga la información al pasajero**. Cómo entra la posición al sistema se decide en [ADR-002](002-protocolo-ingesta-gps.md).

Con la carga estimada (30 posiciones/s de entrada, del orden de 1 000 pasajeros consultando en hora punta), la duda no es si el servidor puede responder, sino cuántas peticiones genera y cuántos bytes viaja por datos móviles.

## Alternativas consideradas

1. **WebSocket con Django Channels.** Actualización inmediata y sin peticiones repetidas. En contra: exige conexiones persistentes, conocimiento de async/ASGI que el equipo no tiene (R-02), y un canal permanente consume datos y batería del pasajero incluso con el mapa quieto.
2. **Server-Sent Events (SSE).** Mejor que WebSocket para este caso, porque el flujo es unidireccional (servidor → cliente) y reconecta solo. En contra: mantiene los mismos requisitos de async/ASGI y no aporta ventaja sobre el polling para este volumen.
3. **Polling cada 10 s a un endpoint de solo lectura que responde desde Redis.** Simple, compatible con PWA, sin conexiones persistentes. En contra: genera peticiones repetidas y el pasajero puede ver datos con hasta ~10 s de antigüedad.

## Decisión
Usaremos **polling cada 10 s** desde la PWA contra un endpoint de solo lectura que responde íntegramente desde Redis. Redis almacena la última posición conocida de cada bus y el ETA precalculado por el módulo de ETA en el momento en que se recibe cada posición.

Con el fin de no castigar los datos móviles del pasajero, la entrega se implementa con tres medidas:

- **Suscripción por ruta:** el pasajero recibe solo los buses de la ruta que está viendo, no los 300. La consulta del mapa acotada a una ruta es el caso de uso principal (RF-06).
- **Respuestas compactas:** identificadores numéricos, coordenadas con precisión limitada a 4 decimales (~11 m) y compresión. La precisión completa se conserva en PostgreSQL.
- **Validación con ETag:** el servidor responde `304 Not Modified` cuando el pasajero ya tiene el estado vigente, de modo que una consulta sin cambios consume solo las cabeceras.

El retraso total percibido es el intervalo de polling más el tiempo de cálculo del ETA. Con el cálculo disparado por cada posición recibida, el peor caso es de ~10 s, dentro de los 15 s de QA-01.

## Consecuencias
**Positivas**
- Implementación simple y fácil de probar con herramientas comunes, sin async ni configuración de servidor de conexiones.
- Las lecturas no cargan PostgreSQL: Redis responde directamente.
- El retraso máximo percibido cumple QA-01 sin necesidad de infraestructura adicional.
- Compatible con PWA y con el modo de datos limitados del pasajero (R-04).
- El endpoint es un snapshot completo, así que el cliente nunca queda con estado corrupto ante una caída.

**Negativas / riesgos**
- Más peticiones que con un canal persistente. Con 1 000 pasajeros consultando, el costo está en el volumen de respuestas, no en la CPU del servidor. Mitigación: suscripción por ruta, compresión y ETag.
- El pasajero puede ver información con hasta ~10 s de antigüedad; visualmente se mitiga mostrando la hora de la última posición de cada bus.
- Ante una caída del VPS (punto único de fallo, R-03) todos los clientes reintentan a la vez. Mitigación: reintento con backoff exponencial y jitter en el cliente, para no producir una tormenta de peticiones.
- Los datos en Redis son de solo lectura para el pasajero: si Redis pierde la caché, el sistema se recupera reconstruyendo desde PostgreSQL, sin pérdida de datos.
- Si Redis se degrada, el endpoint no debe caer. Mitigación: el módulo de seguimiento degrada a lectura directa de PostgreSQL, aceptando mayor latencia antes que dejar el mapa en blanco (QA-02).

## Validación
- Medición del p95 del retraso por etapa (recepción → ETA → entrega) para confirmar que se mantiene en ≤ 15 s con carga de 1 000 pasajeros concurrentes.
- Medición del consumo de datos por sesión de mapa abierta, con el objetivo de mantenerlo por debajo del presupuesto acordado.
- Prueba de comportamiento con un bus sin señal: debe marcarse "sin señal" a los 30 s sin datos, sin afectar la carga del mapa (QA-02).

## Criterio de revisión
Este ADR es falsable. Si las mediciones muestran que el polling no alcanza QA-01 bajo carga real, o que el consumo de datos por sesión resulta inaceptable, se evaluará migrar la entrega a SSE —no a WebSocket, por ser este un flujo unidireccional— **detrás de la misma interfaz de entrega**, lo que permitiría hacerlo sin modificar los demás módulos.
