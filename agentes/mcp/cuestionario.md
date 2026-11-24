# Cuestionario del Laboratorio 11

**1. ¿Qué problema de integración resuelve MCP? Explíquelo con la relación N × M frente a N + M usando su proyecto.**
Sin un estándar, cada agente necesita su propio adaptador para cada fuente. En RutaSIT tenemos 3 consumidores (el agente del Lab 10, VS Code con Copilot y Claude Code) y 3 fuentes útiles (el cálculo de ETA, la detección de desvíos y los documentos del proyecto): serían 3 × 3 = 9 integraciones a mano. Con MCP publicamos las fuentes una vez en el servidor `rutasit` y cada host trae su cliente estándar: 3 + 1 piezas. Cuando agreguemos un cuarto host, no hay que tocar el servidor.

**2. Diferencie host, cliente y servidor. ¿Cuántos clientes tendría un host conectado a tres servidores?**
El host es la aplicación que tiene el LLM y decide qué servidores conectar y qué permisos pedir (VS Code, Claude Code o nuestro `analista_mcp.py`). El cliente es la conexión 1:1 entre el host y un servidor, que traduce las llamadas a JSON-RPC (`HerramientasMCP` usa uno). El servidor expone herramientas, recursos y prompts y no sabe qué LLM lo usa (`rutasit_mcp.py`). Un host conectado a tres servidores tiene tres clientes.

**3. ¿Por qué una consulta de ventas es una herramienta y un ADR es un recurso? ¿Quién decide usar cada uno?**
Una consulta con parámetros que dependen de la pregunta, como `tiempo_llegada(R-07, Plaza de Armas)`, es una herramienta: la elige el modelo, con permiso del usuario. Un ADR es contexto estable identificado por una URI (`rutasit://adr/010`): no calcula nada y lo decide la aplicación (el host), que lo agrega al contexto cuando hace falta. En nuestro analista el host decidió exponer los recursos al modelo mediante `leer_recurso`.

**4. ¿Qué cambió en el ciclo de vida con la especificación 2026-07-28 y por qué facilita desplegar servidores remotos?**
Desapareció el saludo `initialize` y la sesión. Cada petición lleva en `_meta` su versión de protocolo y las capacidades del cliente, y el servidor responde `server/discover`. Como ninguna petición depende de una anterior, cualquier instancia del servidor detrás de un balanceador puede atender cualquier petición. Lo vimos en la traza: el cliente actual empieza con `server/discover`, y el cliente antiguo forzado con `mode="legacy"` empieza con `initialize`; nuestro servidor atiende a los dos.

**5. ¿Qué diferencia hay entre un resultado con isError: true y un error de JSON-RPC? ¿Cuál permite que el agente se corrija?**
`isError: true` es un resultado normal de `tools/call` que dice que la herramienta falló por una razón de negocio, con un mensaje para el modelo ("Ruta desconocida '7'. Valores válidos: R-07, R-12"). Un error de JSON-RPC es una falla del protocolo (método inexistente, recurso desconocido, parámetros mal formados) y lo maneja el cliente. El primero permite que el agente se corrija: en las dos corridas el agente pasó "7", leyó el mensaje y repitió con "R-07".

**6. ¿Por qué las anotaciones de una herramienta son "pistas" y no garantías? ¿Cómo las usó su política?**
Las escribe el propio servidor y nadie las verifica: un servidor malicioso puede marcar como `readOnlyHint=true` una herramienta que borra. Nuestra política deriva de ellas qué herramientas requieren aprobación (`h.herramientas_de_escritura()` → `requieren_aprobacion`), y por eso `reportar_desvio` pide `s`/`n` a una persona. Lo hacemos solo porque el servidor es nuestro y sus pruebas fijan las anotaciones.

**7. Según su E6, ¿cuánto contexto consume su catálogo y qué optimización aplicaron?**
El catálogo inicial ocupaba unos 1151 tokens (4 herramientas). Fusionamos `estado_desvio` dentro de `buses_en_ruta`, quitamos campos que no se usaban y acortamos las descripciones: quedó en unos 805 tokens (−30 %). La misma consulta pasó de 14 a 12 mensajes, de 10 848 a 8 451 bytes y de 6 a 5 pasos, y el agente siguió eligiendo bien.

**8. Describa el envenenamiento de herramientas y tres controles que aplicaría antes de conectar un servidor de terceros.**
Es esconder instrucciones para el modelo en la descripción de una herramienta, que el usuario normalmente no ve. `clima_mcp.py` pide leer `.env`, copiarlo en el parámetro `contexto` y no decírselo al usuario. Controles: leer el catálogo completo y pasarle el auditor antes de conectarlo (marca instrucciones ocultas, pedidos de secretos y textos sin `maxLength`); mantener una lista de servidores aprobados con versión fija, para que una actualización no cambie las descripciones sin revisión; y exigir aprobación humana para toda herramienta que escriba, sin dejar secretos al alcance del agente.
