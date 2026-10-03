# Bitácora de uso de IA — RutaSIT Arequipa

Registro de las interacciones reales del equipo con herramientas de IA durante el
Laboratorio 04. Cada entrada corresponde a un prompt ejecutado y a la respuesta que la
herramienta devolvió. Se documenta también qué verificamos y qué decidimos como equipo.

| # | Fecha | Herramienta | Prompt (resumen) | Qué propuso la IA | Qué verificamos o corregimos | Decisión |
|---|-------|-------------|------------------|-------------------|------------------------------|----------|
| 1 | 02/10/2026 | Claude (Anthropic) | Prompt 1: generar 3 alternativas de estilo arquitectónico para RutaSIT con las restricciones del equipo. | Propuso tres alternativas: **A** monolito modular Django con polling, **B** monolito modular orientado a eventos (Redis + WebSocket/SSE) y **C** microservicios con broker MQTT/Kafka. Recomendó la **B**, con un plan en dos fases, argumentando que el canal persistente resuelve a la vez el ETA de ≤ 15 s y el consumo de datos del pasajero. | Contrastamos la recomendación contra los drivers. La opción B contradice **R-02**: el propio texto admite que el equipo "no domina el stack" async/ASGI, y comprometer R-01 (1 mes). También señalamos que la premisa central de B ("el canal persistente ahorra datos") no fue medida por la IA, sino asumida. Descartamos B y C; el equipo se quedó con un monolito modular con polling. | **Corregida** |
| 2 | 02/10/2026 | Claude (Anthropic) | Prompt 2: crítica adversarial ("abogado del diablo") contra la alternativa recomendada en la entrada 1. | enumeró los supuestos que no se sostienen y 5 riesgos con mitigación: (1) la curva async/Channels consume el mes, (2) punto único de fallo y tormenta de reconexiones, (3) inestabilidad de conexiones en redes móviles, (4) incumplimiento del ETA bajo ráfagas y desorden, y (5) pérdida silenciosa de eventos por Pub/Sub. Añadió una mención aparte: las alertas pueden generar falsos positivos por ruido de GPS. **Cambió su propia recomendación** al cierre: "empezar con A optimizada y tratar B como una mejora condicionada". | La respuesta revoca explícitamente la entrada 1, por lo que la aceptamos como corrección válida. Adoptamos la recomendación revisada (polling con snapshot por ruta, ETag y compresión), que es la que quedó en [ADR-003](../adr/003-actualizacion-tiempo-real.md). Adoptamos las mitigaciones verificables: idempotencia por `timestamp`, marca de tiempo por etapa (recepción → ETA → entrega), snapshot completo más delta, y reintento con backoff y jitter. No adoptamos SSE/WebSocket para el MVP. | **Aceptada** |
| 3 | 02/10/2026 | DeepSeek | Prompt 3: generar el código Mermaid (flowchart TB) del monolito modular. | Devolvió un `flowchart` con los 3 actores, los 5 módulos dentro de un `subgraph` y las dependencias entre módulos: `Ingesta → Seguimiento → ETA → Alertas`, más las conexiones a PostgreSQL, Redis y al proveedor de mapas. El código renderiza correctamente en mermaid.live. | Renderiza bien, pero **no lo adoptamos**. Omite la capa de presentación (API REST + PWA) y, sobre todo, dibuja dependencias directas entre módulos, lo que contradice el aislamiento de módulos de [ADR-001](../adr/001-estilo-arquitectonico.md), donde los módulos se comunican solo por interfaces públicas y ninguno conoce internamente a otro. El diagrama oficial del proyecto (E3, a cargo del Rol B) mantiene la capa de presentación y la de infraestructura, y respeta esa trazabilidad. Conservamos el código de DeepSeek como referencia descartada. | **Corregida** |
| 4 | 03/10/2026 | ChatGPT (OpenAI) | Prompt 4: revisión crítica del ADR-002 (protocolo de ingesta GPS). | Detectó 12 fallas concretas y señaló 3 como bloqueantes: (1) verificar la compatibilidad real del GPS con HTTPS POST, (2) sustituir la afirmación "30 peticiones por segundo caben en un VPS pequeño" por una hipótesis medible, y (3) explicitar reintentos, duplicados, pérdida de conectividad y los límites de lo que el endpoint hace de forma síncrona. También señaló que la fecha del ADR estaba en el futuro. | Aplicamos los 3 puntos bloqueantes y 6 de las fallas secundarias: fecha real (02/10), sección de **Precondiciones** con el hardware GPS como condición bloqueante, criterio de carga medible (≥ 30 req/s, p95 < 300 ms) con sección de **Validación**, idempotencia ante duplicados, definición de "ingesta completada", especificación del payload, precisión en "no requiere introducir un broker adicional" y **Criterio de revisión** que hace el ADR falsable. Agregamos la tercera alternativa que faltaba (HTTPS → Django → cola). Diferimos la autenticación del dispositivo a un ADR de seguridad posterior. | **Aceptada** |
| 5 | 03/10/2026 | Gemini (Google) | Prompt 5: verificar si existe una API pública oficial con las posiciones GPS de los buses del SIT de Arequipa. | Afirmó que **no existe** una API pública, oficial y abierta con posiciones GPS en tiempo real. Respaldó su respuesta con afirmaciones concretas: que el Gobierno Regional y la Municipalidad Provincial implementaron "a inicios de 2026" plataformas web de monitoreo GPS, que SITransporte centraliza los datos para fiscalización, que existen apps de usuarios (SmartBus, Arequipa Bus, SIT Transporte) que consumen endpoints privados, y que Arequipa no publica feed GTFS/GTFS-RT en el portal de datos abiertos del Estado. | **No pudimos confirmar ni desmentir.** Buscamos en el portal nacional de datos abiertos y en fuentes oficiales y no hallamos respaldo para ninguna de las afirmaciones; en particular, no existe fuente verificable que respalde las fechas ni los nombres de las apps. La respuesta mezcla afirmaciones comprobables (la ausencia de GTFS-RT es una hipótesis plausible) con datos concretos sin citar fuente, y contradice a la entrada 1, donde otra IA afirmó lo contrario sobre las plataformas de monitoreo. Por eso la rechazamos **como base de decisión**, no por ser falsa, sino por no ser verificable. | **Rechazada** |

> Los prompts completos se incluyen en la sección "Anexo: prompts", al final de este
> documento. No se incluye información personal ni confidencial en ningún prompt.

## Decisiones del equipo que se derivan de esta bitácora

1. **No se depende de ninguna API externa para el MVP.** La ingesta de posiciones se
   implementa contra la fuente que defina el operador ([ADR-002](../adr/002-protocolo-ingesta-gps.md)),
   con un generador de datos simulados para desarrollo. Si en el futuro apareciera una
   fuente pública, se agregaría como adaptador adicional sin modificar el resto del
   sistema.
2. **La recomendación de una IA no se acepta sin contrastarla con los drivers.** Las
   entradas 1, 3 y 5 muestran tres casos distintos de desviación: sobrearquitectura
   (microservicios, broker, eventos), diagramas que rompen una restricción arquitectónica
   ya decidida, y datos técnicos afirmados sin fuente.
3. **Las IAs se corrigen entre sí y hay que leer la corrección.** La entrada 2 es el caso
   más claro: la herramienta que recomendó la arquitectura más compleja fue la misma que
   la desmintió al día siguiente.

## Anexo: prompts

Los cinco prompts se transcriben tal como se enviaron a cada herramienta.

### Prompt 1 — Generación de alternativas (Claude, 02/10/2026)

```text
Actúa como arquitecto de software senior con experiencia en sistemas para PYMES.
Contexto: plataforma "RutaSIT Arequipa" para seguir en tiempo real los buses del Sistema
Integrado de Transporte. 300 buses envían su posición cada 10 s; los pasajeros ven el mapa
y el tiempo estimado de llegada (ETA); el operador recibe alertas de desvío o congestión.
Restricciones: 3 developers con experiencia en Python/Django, presupuesto bajo (un VPS),
MVP en 1 mes, pasajeros con celulares y datos móviles limitados. El ETA debe estar
disponible en ≤ 15 s tras recibir la posición.
Tarea: propón 3 alternativas de estilo arquitectónico. Para cada una indica fortalezas,
debilidades, riesgos y qué atributos de calidad favorece o penaliza.
Formato: tabla comparativa en Markdown y, al final, tu recomendación justificada.
No inventes APIs ni capacidades de servicios; si no estás seguro, indícalo.
```

### Prompt 2 — Crítica adversarial (Claude, 02/10/2026)

Enviado en la misma conversación que el Prompt 1, para que la herramienta criticara su
propia recomendación.

```text
Ahora actúa como "abogado del diablo". Critica duramente la alternativa que recomendaste:
¿qué supuestos no se cumplen con nuestras restricciones?, ¿qué podría fallar en producción?,
¿qué costo oculto tiene? Enumera los 5 riesgos más graves y, para cada uno, una táctica
arquitectónica de mitigación.
```

### Prompt 3 — Generación del Mermaid (DeepSeek, 02/10/2026)

```text
Genera el código Mermaid (flowchart TB) de un monolito modular para RutaSIT con actores
Bus, Pasajero y Operador; módulos Ingesta, Seguimiento, ETA, Alertas y Rutas; PostgreSQL,
Redis y un proveedor de mapas externo. Usa subgraph para el monolito y muestra la dirección
de las dependencias. Devuelve solo el código.
```

### Prompt 4 — Revisión del ADR-002 (ChatGPT, 03/10/2026)

Se envió el borrador del ADR-002 en su versión inicial, es decir, antes de las
correcciones que derivaron de esta misma revisión.

```text
Revisa este ADR como revisor crítico: ¿se entiende por sí solo?, ¿las alternativas son
reales?, ¿las consecuencias negativas son honestas? Lista fallas concretas y propón mejoras.

---
# ADR-002: Recibir las posiciones GPS por HTTPS (POST) en lugar de MQTT

- Estado: Aceptado
- Fecha: 2026-10-03
- Decisores: <nombres de los 3 integrantes>

## Contexto
RF-01 exige recibir la posición de 300 buses cada 10 s (30 mensajes por segundo), con ETA
en ≤ 15 s (QA-01). El equipo tiene 3 developers de Django (R-02), un solo VPS (R-03) y
1 mes de plazo (R-01).

## Alternativas consideradas
1. MQTT con un broker (por ejemplo, Mosquitto): protocolo liviano pensado para IoT, pero
   agrega un componente que operar y aprender.
2. HTTPS POST con JSON al endpoint de ingesta de Django: sin componentes nuevos, se prueba
   con herramientas comunes.

## Decisión
Usaremos HTTPS POST con JSON (`bus_id`, `lat`, `lon`, `timestamp`) hacia el módulo de
Ingesta. 30 peticiones por segundo caben en un VPS pequeño con Nginx y Django.

## Consecuencias
- Positivas: sin broker adicional; se prueba con curl y scripts; encaja con el stack del
  equipo.
- Negativas / riesgos: más sobrecarga por mensaje que MQTT; si los GPS físicos solo
  soportan MQTT o TCP habría que agregar un adaptador (verificar con el operador). Se
  medirá con una prueba de carga de 30 pos/s.
```

### Prompt 5 — Verificación de un dato técnico (Gemini, 03/10/2026)

```text
¿Existe una API pública oficial con las posiciones GPS de los buses del SIT de Arequipa?
Si no estás seguro, dilo claramente y no inventes URLs ni endpoints.
```
