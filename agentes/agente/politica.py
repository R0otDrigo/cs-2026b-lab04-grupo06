"""Guardrails: qué puede hacer el agente, cuántas veces y con qué aprobación."""
import re
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class Decision:
    permitido: bool
    motivo: str = ""
    humano: Optional[str] = None                # "s" o "n" cuando una persona aprobó o rechazó


@dataclass
class Politica:
    herramientas_permitidas: set = field(default_factory=lambda: {
        "listar_archivos", "leer_archivo", "buscar", "ejecutar_pruebas", "editar_archivo", "ejecutar_comando"})
    comandos_permitidos: tuple = (r"^python -m pytest\b", r"^radon cc\b", r"^lint-imports\b", r"^git (status|diff)\b")
    # RutaSIT tiene sus pruebas en test/ (Labs 05-09) y las de los issues en tests/: ambas protegidas.
    rutas_protegidas: tuple = ("tests/", "test/")
    max_pasos: int = 15
    # Humano en el circuito. Antes era un atributo de clase sin tipo y no se podía pasar al constructor.
    aprobar_edicion: Optional[Callable[[dict], bool]] = None

    def evaluar(self, accion: str, args: dict, paso: int) -> Decision:
        if paso > self.max_pasos:
            return Decision(False, f"Se alcanzó el máximo de {self.max_pasos} pasos")
        if accion not in self.herramientas_permitidas:
            return Decision(False, f"Herramienta no permitida: {accion}")
        if accion == "ejecutar_comando":
            cmd = args.get("comando", "")
            if not any(re.search(p, cmd) for p in self.comandos_permitidos):
                return Decision(False, f"Comando fuera de la lista permitida: {cmd!r}")
        if accion == "editar_archivo":
            ruta = str(args.get("ruta", "")).replace("\\", "/").lstrip("./")
            if ruta.startswith(self.rutas_protegidas):
                return Decision(False, f"Ruta protegida: {ruta}")
            if self.aprobar_edicion is not None:
                if not self.aprobar_edicion(args):
                    return Decision(False, "El revisor humano rechazó la edición", humano="n")
                return Decision(True, humano="s")
        return Decision(True)
