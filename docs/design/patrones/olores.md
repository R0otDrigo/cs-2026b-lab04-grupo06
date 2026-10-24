# Olores detectados y patrón propuesto (Lab 07)

Flujo crítico refactorizado: **consultar el tiempo de llegada (ETA)** de un bus a un paradero
(el mismo del diagrama de secuencia del Lab 05). Archivo analizado: `src/rutasit/antes/servicio.py`.
Salida de `radon cc -s`: `ServicioEta.consultar_eta` = **D (22)**.

| # | Líneas | Olor | Patrón propuesto por la IA | Principio SOLID | Costo de aplicarlo | Decisión del equipo |
|---|--------|------|----------------------------|-----------------|--------------------|---------------------|
| 1 | 61-81 | `if/elif` por algoritmo de ETA que crece con cada algoritmo nuevo | Strategy + Factory | O (abierto/cerrado) | 1 interfaz + 1 clase por algoritmo | Aceptado |
| 2 | 35-55 | El servicio conoce los detalles de cada operador GPS (dict vs tupla, km/h vs m/s, grados vs microgrados) | Adapter | D (inversión de dependencias) | 1 adaptador por operador | Aceptado |
| 3 | 36-43, 45-53, 67-73 | Bloques de reintentos duplicados (GPS A, GPS B, mapas) | Decorator | S (responsabilidad única) | 1 clase envoltorio | Aceptado |
| 4 | 26-32 | Condicionales sobre `viaje.estado` (máquina de estados del Lab 05 escrita con `if`) | State | L (sustitución) / O | 1 clase por estado (5) | Aceptado: coincide con `estados-viaje.mmd` del Lab 05 |
| 5 | 83-85 | El servicio arma a mano los avisos al pasajero y al operador | Observer | S / O | 1 publicador + suscriptores | Aceptado |
| 6 | 88-97 | Validaciones de la salida del LLM mezcladas en un solo método | Chain of Responsibility (+ Adapter + Decorator para el LLM) | S / O | 1 clase por guardrail | Aceptado |
| 7 | — | "`FabricaGps` debería ser Singleton" | Singleton | — | — | **Rechazado**: estado global; impide inyectar GPS simulados en las pruebas |
| 8 | — | "Usar Abstract Factory para crear familias de GPS y mapas" | Abstract Factory | — | — | **Rechazado**: no hay familias de productos; sería sobreingeniería |
