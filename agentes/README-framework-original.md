# Laboratorio 10 — Sistemas agénticos (Construcción de Software 2026-B, EPIS-UNSA) — v2

Mini framework de agentes (~300 líneas de Python) para resolver el issue #27 de AgroConecta.

    pip install pytest radon
    python -m pytest -q pruebas_agente   # pruebas del contrato, la política y el sandbox
    python orquestador.py                # planificador → [ejecutor ↔ revisor] (actor-crítico, máx. 2 rondas) → humano
    python agente/traza.py               # trazas JSONL → trazas/trayectoria.mmd + métricas

- `agente/nucleo.py`: bucle ReAct como máquina de estados. `agente/contrato.py`: validación de cada decisión.
- `agente/herramientas.py` (sandbox), `agente/politica.py` (guardrails), `agente/modelos.py` (Grabado, Interactivo, Anthropic).
- `trabajo_original/`: código con el bug, la prueba del issue y un comentario con inyección indirecta (no lo ejecute).
- `trayectorias/`: decisiones grabadas (ronda 1 y ronda 2). `diagramas/`: fuentes Graphviz, PlantUML y matplotlib de la guía.
