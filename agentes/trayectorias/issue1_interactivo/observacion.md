# Corrida interactiva E2: issue 1

El 20/11/2026 se ejecutó `python orquestador.py --issue 1 --modo unico --interactivo --corrida issue1_interactivo` desde `agentes/`. ChatGPT produjo seis decisiones a partir del objetivo y de cada observación real de las herramientas; se pegaron en `ModeloInteractivo` sin corregirlas a mano. El contrato rechazó **0** decisiones.

El agente editó `src/rutasit/gps.py` únicamente dentro de `agentes/trabajo/`. Las cuatro pruebas del issue 1 pasaron. La suite del sandbox terminó con **3 failed, 68 passed, 1 xfailed**; los tres fallos son de los issues 2 y 3. La traza y el diagrama Mermaid están en `agentes/trazas/issue1_interactivo/`.
