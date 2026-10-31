# ADR-008: Aislamiento por operador y firma HMAC de los dispositivos GPS

- Estado: Aceptado
- Fecha: 2026-10-29
- Decisores: Estefanero Palma Rodrigo, Sullca Mamani Mauro Snayder y Riveros Vilca Alberth Edwar

## Contexto
Con 1200 buses se incorporan varios operadores que no deben ver los datos de los demás (QA-05). Además, el ADR-002 dejó la autenticación de los dispositivos GPS para "un ADR de seguridad posterior" (QA-06). Restricciones: 1 mes y 3 developers (R-01, R-02); la ingesta no maneja datos personales (R-05).

## Alternativas consideradas
1. Una base de datos por operador. Rechazada: operación compleja en un solo VPS.
2. Un esquema por operador. Rechazada por ahora (se revisa si son más de 20 operadores).
3. Columna `operador_id` + filtro obligatorio en el repositorio + RLS de PostgreSQL + operador en el token. Aceptada.
4. API key fija por operador. Rechazada: si se filtra vale siempre y no frena reenvíos.
5. Certificado por dispositivo (mTLS). Rechazada para el MVP: administrar 1200 certificados.
6. Firma HMAC-SHA256 con secreto por operador, marca de tiempo (±60 s) y límite de tasa en Nginx. Aceptada.

## Decisión
Usaremos **columna operador_id con filtro obligatorio** en el repositorio (no existe forma de consultar sin operador) y **RLS en PostgreSQL** como segunda defensa. Los dispositivos firmarán cada posición con **HMAC-SHA256** (secreto por operador) incluyendo la marca de tiempo; la ingesta rechaza mensajes con firma inválida o de más de 60 s. Nginx limitará la tasa de solicitudes por dispositivo (`limit_req`). Se agrega el componente **Módulo Seguridad** al modelo C4.

## Consecuencias
- Positivas: 0 filas ajenas en 200 consultas y 0 de 1000 alteraciones aceptadas (FF-10 y FF-11); agregar un operador es una fila de configuración.
- Negativas / riesgos: las políticas RLS aún no se prueban en integración continua (R2); los relojes de los GPS deben estar sincronizados ±60 s; el secreto es por operador, no por dispositivo (R7): hay que rotarlo.
- Evidencia: add/iteracion-3.md, fitness/aislamiento.py, fitness/auth_gps.py, FF-10 y FF-11.
