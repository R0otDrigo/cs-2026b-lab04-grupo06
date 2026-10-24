# ADR-005: Patrones de diseño en el flujo "consultar el tiempo de llegada (ETA)"

**Estado:** Aceptado (23/10/2026)

## Contexto
`ServicioEta.consultar_eta()` tenía complejidad ciclomática 22 (D). Cada operador de GPS, algoritmo de ETA o interesado
nuevo obligaba a modificar el servicio. La salida del LLM (explicación del retraso) no es confiable.

## Decisión
Adapter + Strategy + Factory para GPS y ETA; Decorator para reintentos, caché y respaldo; State para el ciclo de vida del
Viaje (Lab 05); Observer para los avisos; Chain of Responsibility para los guardrails de la IA. Se rechazan Singleton y
Abstract Factory (ver `docs/design/patrones/olores.md`).

## Consecuencias
(+) Complejidad máxima 5 (antes 22); nuevos operadores, algoritmos y suscriptores sin modificar el servicio; IA probable sin API.
(-) 266 líneas frente a 85 y más indirección: el equipo debe conocer los patrones.
