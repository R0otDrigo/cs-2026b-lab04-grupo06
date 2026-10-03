# ADR-002: Recibir las posiciones GPS por HTTPS (POST) en lugar de MQTT

- Estado: Aceptado
- Fecha: 2026-10-02
- Decisores: Estefanero Palma Rodrigo, Sullca Mamani Mauro Snayder, Riveros Vilca Alberth Edwar
- Drivers relacionados: RF-01, QA-01, QA-02, R-01, R-02, R-03

## Contexto
RF-01 exige recibir la posición de 300 buses cada 10 s. La carga nominal es de **30 solicitudes por segundo**, y QA-01 exige que el ETA esté disponible en ≤ 15 s (p95) tras recibir la posición. El equipo son 3 developers con experiencia en Python/Django (R-02), hay un solo VPS (R-03) y el plazo del MVP es 1 mes (R-01).

Con esta carga, la ingesta no es el cuello de botella: 30 req/s con payloads de ~100-200 bytes es tráfico trivial. Lo que sí condiciona el diseño es el Fan-out hacia los pasajeros y el cálculo del ETA dentro de la ventana de 15 s.

Este ADR se limita a **cómo entra** la posición al sistema. Cómo se propaga al pasajero se decide en [ADR-003](003-actualizacion-tiempo-real.md).

## Precondiciones
Antes de implementar, se debe verificar que el modelo de GPS que instalará el operador sea capaz de enviar datos por HTTPS POST sobre TLS. Si el dispositivo solo soporta MQTT o TCP propietario, **este ADR debe revisarse** y agregar un adaptador. Esta verificación es bloqueante: condiciona la viabilidad de la decisión.

## Alternativas consideradas

1. **MQTT con un broker** (por ejemplo, Mosquitto). Protocolo liviano pensado para IoT, con modelo pub/sub y niveles de QoS. A favor: menor sobrecarga por mensaje y idiomático para dispositivos. En contra: requiere operar y aprender un componente adicional, y su utilidad real depende de las capacidades del hardware GPS que se confirme en las precondiciones.
2. **HTTPS POST con JSON al endpoint de ingesta de Django.** Sin componentes nuevos: se prueba con `curl` o cualquier script y encaja con el stack del equipo. En contra: más sobrecarga por mensaje que MQTT.
3. **HTTPS POST encolado internamente** (HTTPS → Django → Redis/cola → procesamiento asíncrono). Evita que la ingesta se bloquee si el cálculo de ETA o la persistencia se demora. Se descarta para el MVP por su complejidad operativa adicional, pero se conserva documentada como opción de escalamiento.

## Criterios de decisión
- Compatibilidad con los dispositivos GPS disponibles (ver precondiciones).
- Capacidad de sostener ≥ 30 req/s con p95 de latencia de ingesta por debajo de 300 ms.
- Cumplimiento de QA-01: ETA disponible en ≤ 15 s.
- Complejidad operativa tolerable para 3 developers sin DevOps (R-02).
- Tiempo de implementación ≤ 1 mes (R-01).

## Decisión
Usaremos **HTTPS POST con JSON** hacia el módulo de Ingesta.

Payload: `{ "bus_id": <int>, "lat": <float, -90..90>, "lon": <float, -180..180>, "timestamp": <ISO 8601 UTC> }`. La especificación completa del contrato de datos (unidades, precisión, versión) se detalla en la documentación de la API del módulo de Ingesta.

Definiciones operativas:
- La ingesta se considera **completada** cuando el mensaje ha sido validado y persistido de forma duradera en PostgreSQL. El cálculo del ETA ocurre después, sobre datos ya persistidos, de modo que la ingesta nunca queda bloqueada por la lógica de ETA.
- El endpoint **no** realiza cálculos pesados de forma síncrona.

## Consecuencias
**Positivas**
- No requiere introducir un broker de mensajería adicional.
- Se prueba con `curl` y scripts, sin infraestructura nueva que aprender.
- Encaja con el stack del equipo (R-02) y con el plazo de un mes (R-01).
- El mismo endpoint sirve para datos de prueba en desarrollo y producción.

**Negativas / riesgos**
- Mayor sobrecarga por mensaje que MQTT (cabeceras HTTP, establecimiento y mantenimiento de TLS).
- Los reintentos del dispositivo pueden producir **mensajes duplicados**. Mitigación: procesamiento idempotente por `bus_id` + `timestamp`, descartando posiciones anteriores a la última conocida.
- Debe definirse timeouts y política de reintentos; si el endpoint demora, los dispositivos pueden acumular posiciones y enviarlas en ráfaga fuera de orden. Mitigación: cola acotada donde solo importa lo último por bus.
- El procesamiento síncrono de la petición sigue exposiendo la ingesta a la carga de PostgreSQL. Mitigación: queries indexadas y prueba de carga antes del MVP.
- El acceso al endpoint requiere autenticación del dispositivo, validación de `timestamp` y rate limiting. **No se resuelve en este ADR**: el mecanismo de autenticación se definirá en un ADR de seguridad posterior.
- Un único VPS es un punto único de fallo (R-03). Mitigación: backups automáticos y procedimiento de restauración probado; no se contemplate alta disponibilidad en el MVP.

## Validación
- Prueba de carga de ≥ 30 req/s sostenidas durante 10 minutos, midiendo p95 y p99 de latencia de ingesta, sin pérdida de mensajes.
- Prueba de reintentos y de caída temporal del servidor, verificando ausencia de duplicados en la base de datos.
- Medición del retraso por etapa (recepción → persistencia → ETA → entrega) con alerta si el p95 se acerca a los 15 s de QA-01.

## Criterio de revisión
Este ADR es falsable. Si la prueba de carga no alcanza 30 req/s sostenidas manteniendo QA-01, o si la precondición de hardware resulta falsa, se evaluará introducir procesamiento asíncrono (alternativa 3) o un broker MQTT, y este documento se reabrirá.
