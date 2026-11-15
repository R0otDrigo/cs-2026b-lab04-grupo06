"""Generador de criterios de aceptacion (Lab 09): el prompt como codigo.

Se usa DETRAS del puerto ProveedorLLM del Lab 07 (rutasit.ia): este modulo no conoce ningun SDK.
Aplica la defensa en capas de la guia (Figura 4):
  capa 1  delimitadores <historia> y neutralizacion de etiquetas dentro de la historia (sanitizar)
  capa 2  instruccion explicita en el prompt (prompts/criterios/v5.txt)
  capa 3  validacion de la salida con JSON Schema y reglas de coherencia
  capa 4  minimo privilegio: el metodo solo DEVUELVE datos; nunca ejecuta acciones por su cuenta
  capa 5  revision humana (el Product Owner revisa antes de importar a Jira; ver README)
"""
from __future__ import annotations

import json
import pathlib

from jsonschema import ValidationError, validate

from rutasit.ia import ProveedorLLM

RAIZ = pathlib.Path(__file__).resolve().parents[2]
CARPETA_PROMPTS = RAIZ / "prompts" / "criterios"


class SalidaInvalida(Exception):
    """La respuesta del LLM no cumple el contrato: se descarta y se registra."""


def sanitizar(historia: str) -> str:
    """Capa 1: una historia no puede cerrar la etiqueta <historia> ni abrir otras.
    Se reemplazan < y > por los signos tipograficos ‹ y ›."""
    return historia.replace("<", "‹").replace(">", "›")


def rellenar(plantilla: str, id_historia: str, historia: str) -> str:
    return plantilla.replace("{{id}}", id_historia).replace("{{historia}}", historia)


class GeneradorCriterios:
    def __init__(self, proveedor: ProveedorLLM, version: str = "v5",
                 carpeta: pathlib.Path = CARPETA_PROMPTS, sanitizar_entrada: bool = True):
        self._proveedor = proveedor                       # Strategy: Claude, otro modelo o grabado
        self._plantilla = (carpeta / f"{version}.txt").read_text(encoding="utf-8")
        self._esquema = json.loads((carpeta / "esquema.json").read_text(encoding="utf-8"))
        self._sanitizar = sanitizar_entrada
        self.version = version

    def construir_prompt(self, id_historia: str, historia: str) -> str:
        texto = sanitizar(historia) if self._sanitizar else historia
        return rellenar(self._plantilla, id_historia, texto)

    def generar(self, id_historia: str, historia: str) -> dict:
        texto = self._proveedor.completar(self.construir_prompt(id_historia, historia))
        try:
            criterios = json.loads(texto)
            validate(criterios, self._esquema)            # capa 3: contrato
        except (json.JSONDecodeError, ValidationError) as e:
            raise SalidaInvalida(f"{self.version}/{id_historia}: {str(e).splitlines()[0]}") from e
        self._exigir_coherencia(id_historia, criterios)
        return criterios

    @staticmethod
    def _exigir_coherencia(id_historia: str, c: dict) -> None:
        if c["historia_id"] != id_historia:
            raise SalidaInvalida(f"{id_historia}: historia_id distinto ({c['historia_id']})")
        if not c["invest_ok"] and (c["escenarios"] or not c["preguntas"]):
            raise SalidaInvalida(f"{id_historia}: una historia rechazada debe traer preguntas y 0 escenarios")
        tipos = {e["tipo"] for e in c["escenarios"]}
        if c["invest_ok"] and not ("exito" in tipos and tipos & {"error", "borde"}):
            raise SalidaInvalida(f"{id_historia}: falta un escenario de exito o uno de error o borde")
