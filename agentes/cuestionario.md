# Cuestionario del Laboratorio 10

**1. ¿Qué diferencia a un agente de un flujo de trabajo fijo? Dé un ejemplo de su proyecto en el que un flujo de trabajo sea mejor opción.**
En un flujo de trabajo el programador fija los pasos; en un agente el modelo decide el siguiente paso según lo que observa. En RutaSIT, regenerar los diagramas C4 (`diagramas.yml`) o correr las evaluaciones de prompts del Lab 09 (`prompts.yml`) son siempre los mismos pasos: ahí un workflow de GitHub Actions es más barato, predecible y no necesita un modelo. Los issues sí necesitan un agente, porque no se sabe de antemano qué archivo tocar.

**2. Elija dos arquetipos de agentes y explique cuál usaría para cada uno de sus tres issues.**
ReAct y planificador-ejecutor. Para el issue 1 (GPS sin datos) y el issue 3 (desvío en curvas) basta ReAct: el traceback o una búsqueda llevan directo al archivo y el cambio es local. Para el issue 2 (ETA negativo) usaríamos planificador-ejecutor con un crítico, porque el cambio altera el tipo de retorno de una función que otros módulos usan; el plan y la revisión obligan a mirar a los llamadores.

**3. Describa la máquina de estados de su agente. ¿Qué guardia evita que el agente se ejecute indefinidamente?**
Decidiendo → ValidandoContrato → EvaluandoPolitica (con EsperandoAprobacion para ediciones) → Ejecutando → Observando → Decidiendo, con dos estados finales: Finalizado y LimiteAlcanzado. La guardia `[paso > max_pasos]` de la política (12 para el ejecutor, 8 para el revisor, 2 para el planificador) y el `range(1, max_pasos + 2)` del bucle evitan la ejecución indefinida; además el actor-crítico tiene un máximo de 2 rondas.

**4. ¿Qué es un contrato estructurado y qué ocurre en su agente cuando el modelo lo incumple? Dé un ejemplo de su bitácora.**
Es la forma exacta que debe tener cada decisión: `{"pensamiento", "accion", "args"}` o `{"pensamiento", "final"}`, con una herramienta del catálogo y `args` como objeto. Si no se cumple, el agente no actúa: registra `CONTRATO_INVALIDO` y devuelve "ERROR DE CONTRATO: ..." como observación para que el modelo se corrija. En la bitácora (entrada 3) encontramos que `ModeloInteractivo` se caía con texto no JSON en lugar de dejar que el contrato lo rechace; lo corregimos y lo probamos con `test_interactivo_no_se_cae_si_lo_pegado_no_es_json`. En nuestras grabaciones el contrato no rechazó ninguna decisión.

**5. ¿Qué tipo de memoria agregó en E4 y qué efecto tuvo en los pasos y el contexto?**
Una memoria de notas (pizarra) con `anotar` y `leer_notas` en `notas.md`, junto con la herramienta `mapa_repo`. En el issue 3 el agente usó 10 pasos y 13 682 caracteres, contra 9 pasos y 9 391 caracteres sin ellas: no redujo pasos ni contexto. Las notas sirven sobre todo para pasar información entre rondas, porque el ejecutor de la ronda 2 empieza con un historial nuevo.

**6. Según su E5, ¿compensó el bucle actor-crítico su costo adicional? Relacione su respuesta con el principio de parsimonia.**
En el issue 2 sí: el revisor encontró un `TypeError` en `consultar_eta()` que el agente único dejó pasar, a cambio de 2,9 veces más pasos y 4,5 veces más contexto. Por parsimonia no lo usaríamos siempre: en los issues 1 y 3, con cambios locales, un agente único y la aprobación humana bastan. Reservamos el actor-crítico para cambios que alteran un contrato público.

**7. Explique el exceso de agencia y cómo lo evitaron con el mínimo privilegio por rol.**
Es dar al agente más herramientas, permisos o autonomía de los necesarios (OWASP LLM06). Cada rol tiene su política: el planificador no tiene herramientas; el revisor solo lee (`ver_cambios`, `leer_archivo`, `buscar`, `listar_archivos`, `ejecutar_pruebas`); el ejecutor puede editar, pero no `test/` ni `tests/`, y sus comandos están en una lista permitida. En el issue 3 el agente intentó `python -c` y la política lo bloqueó; decidimos no agregarlo a la lista (bitácora, entrada 6).

**8. ¿En qué rol humano dejaría hoy a su agente y qué evidencia necesitaría para avanzar al siguiente?**
En revisor: el agente edita en el sandbox y una persona aprueba cada edición y el Pull Request. Para pasar a colaborador necesitaríamos 20 ediciones aprobadas seguidas sin un rechazo, 0 regresiones y 0 intentos de salir del sandbox en las trazas. Hoy tenemos 2 ediciones aprobadas y un error encontrado por el revisor, así que no alcanza (ver `delegacion.md`).
