# ADR-011: Exponer RutaSIT mediante un servidor MCP

- Estado: Aceptado
- Fecha: 2026-11-23
- Decisores: Estefanero Palma Rodrigo, Sullca Mamani Mauro Snayder y Riveros Vilca Alberth Edwar

## Contexto
En el Lab 10 las herramientas del agente estaban escritas dentro de su propio código. El equipo también quiere consultar buses, tiempos de llegada y desvíos desde el asistente del IDE (VS Code con Copilot, Claude Code) sin reescribir esa lógica para cada uno. Ya existen las reglas aprobadas en código: el ETA sobre la ruta (`rutasit.llegada`, HU-01) y la detección de desvíos (`rutasit.desvio`, RF-04).

## Alternativas consideradas
1. API REST directa. Rechazada por ahora: cada host necesitaría un adaptador propio para describir las operaciones al modelo y no habría un catálogo descubrible ni anotaciones de escritura.
2. Function calling dentro del agente (como en el Lab 10). Rechazada: las herramientas solo sirven a ese agente; el IDE tendría que duplicarlas.
3. Servidor MCP con transporte Streamable HTTP. Pospuesta: requiere autenticación (OAuth 2.1) y un despliegue que todavía no tenemos; queda para el reto o un laboratorio posterior.
4. Servidor MCP con transporte stdio y el SDK oficial de Python. Aceptada.

## Decisión
- Servidor `rutasit` (`agentes/mcp/servidor_mcp/rutasit_mcp.py`), SDK `mcp>=2`, protocolo 2026-07-28 (acepta también clientes 2025 con `initialize`), transporte stdio.
- Se expone: 2 herramientas de lectura (`buses_en_ruta`, `tiempo_llegada`) y una sola de escritura, `reportar_desvio`, que solo crea `reportes/DESVIO-NN.md`; 3 recursos (`rutasit://rutas`, `rutasit://reglas`, `rutasit://adr/{numero}`); 2 prompts (`aviso_usuarios` y `criterios_aceptacion`, el v5 del Lab 09).
- No se expone: cambiar el estado de un viaje, editar rutas ni notificar a pasajeros.
- La lógica no se duplica: el servidor llama a `rutasit.llegada` y `rutasit.desvio`; los datos de la flota son ficticios.
- Controles: anotaciones explícitas en todas las herramientas; `ToolError` con los valores válidos; `maxLength` en todos los textos; la escritura abre en modo `"x"` y exige un bus desviado según RF-04; la plantilla de ADR solo acepta 3 dígitos; sin secretos en el código ni en `.vscode/mcp.json`/`.mcp.json`; aprobación de la escritura en el agente; aprobación en el host pendiente de verificación; auditor en la CI.

## Consecuencias
- Positivas: el agente del Lab 10 usa el servidor sin cambiar su núcleo (adaptador `HerramientasMCP`); incluye configuraciones para VS Code y Claude Code, pendientes de verificación en esos hosts; 25 pruebas de contrato sin LLM ni red; el catálogo optimizado ocupa ~808 tokens (−30 %).
- Negativas / riesgos: arrancar el servidor por stdio tomó unos 1089 ms en la reproducción local; las anotaciones son pistas en las que confiamos solo porque el servidor es nuestro; el auditor por patrones no detecta instrucciones redactadas de otra forma; la especificación cambia rápido y los hosts van atrasados.
- Evidencia: `agentes/mcp/protocolo.md`, `agentes/mcp/seguridad.md`, `agentes/mcp/uso-en-host.md`, `agentes/mcp/trazas/`.
