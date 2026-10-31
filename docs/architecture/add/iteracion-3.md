# Iteración 3 de ADD — Seguridad (QA-05 y QA-06)

## 1–3. Entradas, objetivo y elemento
Al crecer de 300 a 1200 buses se incorporan varios operadores (empresas de transporte) con sus propios GPS (Lab 07: operadores A y B). Objetivo: **QA-05** (aislamiento entre operadores) y **QA-06** (autenticación de los dispositivos GPS). El ADR-002 dejó la autenticación para "un ADR de seguridad posterior": esta iteración lo cierra. Elemento que se refina: nuevo componente **Módulo Seguridad** y la base de datos. Riesgo que mitiga: **R2** y **R7**.

> **Supuesto a confirmar:** que el crecimiento incluya varios operadores que no deben ver los datos de los demás.

## 4. Conceptos de diseño evaluados (el atributo no se simula: comparación de alternativas)
**Aislamiento entre operadores (QA-05)**
| Alternativa | Aislamiento | Costo de agregar un operador | Decisión |
|-------------|-------------|------------------------------|----------|
| Una base de datos por operador | Muy alto | Alto: crear BD, migrar y desplegar | Rechazada: varias bases en un VPS; operación compleja |
| Un esquema por operador | Alto | Medio: migraciones por esquema | Rechazada por ahora; se revisa si son más de 20 operadores |
| **Columna `operador_id` + filtro obligatorio en el repositorio + RLS de PostgreSQL + operador en el token** | Alto si está bien configurado | Bajo: una fila de configuración | **Aceptada** (genera el riesgo R2) |

**Autenticación de dispositivos (QA-06)**
| Alternativa | Seguridad | Costo | Decisión |
|-------------|-----------|-------|----------|
| API key fija por operador | Baja: si se filtra, vale siempre; no frena reenvíos | Muy bajo | **Rechazada** |
| Certificado por dispositivo (mTLS) | Muy alta | Alto: administrar 1200 certificados en 1 mes | Rechazada para el MVP (plan B) |
| **Firma HMAC-SHA256 con secreto por operador + marca de tiempo (±60 s) + límite de tasa en Nginx** | Alta | Bajo | **Aceptada** |

## 5. Decisión
Ver [ADR-008](../adr/008-seguridad-aislamiento-y-firma.md). Prototipos probados: `fitness/aislamiento.py` y `fitness/auth_gps.py`.

## 6–7. Evidencia
| Fitness function | Qué comprueba | Resultado |
|------------------|---------------|-----------|
| FF-10 | 200 consultas alternadas de los operadores A y B (600 buses cada uno) devuelven 0 filas ajenas; el repositorio no permite consultar sin operador | Pasa |
| FF-11 | Un mensaje válido se acepta; **0 de 1000** alteraciones se aceptan; un mensaje de 120 s de antigüedad o con el secreto de otro operador se rechaza | Pasa |

**Límite de la evidencia.** El filtro obligatorio por operador está probado con una base de datos de prueba (SQLite). Las políticas **RLS de PostgreSQL** (segunda defensa) aún no se prueban en integración continua porque el workflow no levanta PostgreSQL: queda como riesgo R2 con la mitigación de probarlas en un entorno de pruebas antes de publicar.

## Trade-offs aceptados
- Los relojes de los GPS deben estar sincronizados dentro de ±60 s; un reloj desfasado produciría rechazos falsos.
- Un secreto por operador (no por dispositivo): si se filtra, afecta a todos los buses de ese operador. Se mitiga con rotación y límite de tasa.
