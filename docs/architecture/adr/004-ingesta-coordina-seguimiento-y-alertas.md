# ADR-004: Ingesta coordina a Seguimiento y Alertas para evitar una dependencia cíclica

- Estado: Aceptado
- Fecha: 2026-10-10
- Decisores: Rodrigo Estefanero, Mauro Sullca y Alberth Riveros

## Contexto
Al dibujar el diagrama de paquetes (Lab 05, E5) vimos que Seguimiento necesitaba avisar a Alertas
cuando un viaje se desvía, y Alertas necesitaba leer los viajes de Seguimiento. Eso forma un ciclo
(seguimiento ↔ alertas) y rompe la regla de ADR-001: los módulos se comunican por interfaces
públicas y no deben depender unos de otros en círculo. Afecta a QA-03 (modificabilidad: agregar
una regla de alerta en 2 días-persona o menos sin tocar otros módulos).

## Alternativas consideradas
1. Seguimiento llama directamente a Alertas: simple, pero crea el ciclo.
2. Seguimiento define un puerto de aviso y Alertas lo implementa: elimina el ciclo, pero agrega una interfaz más para algo pequeño.
3. Ingesta, que recibe cada posición, llama primero a Seguimiento y luego a Alertas: sin ciclos y sin interfaces nuevas.

## Decisión
Usaremos la alternativa 3. El módulo Ingesta registra la posición en Seguimiento y, si el viaje quedó
DESVIADO, llama a Alertas. Seguimiento no depende de Alertas; Alertas solo lee `Viaje`.

## Consecuencias
- Positivas: el diagrama de paquetes no tiene ciclos (C4); agregar una regla de alerta toca solo Alertas e Ingesta.
- Negativas / riesgos: Ingesta queda con más responsabilidad y puede crecer; si pasa de 3 llamadas a otros módulos habrá que replantear el puerto de la alternativa 2.
