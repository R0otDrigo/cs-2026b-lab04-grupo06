"""IA aislada: Strategy + Adapter + Decorator + Chain of Responsibility."""
from abc import ABC, abstractmethod


class ProveedorLLM(ABC):
    """Puerto: el dominio solo conoce esta interfaz, no el SDK de ningun proveedor."""

    @abstractmethod
    def completar(self, prompt: str) -> str: ...


class ClaudeAdapter(ProveedorLLM):
    """ADAPTER. En produccion el cliente real se crea con una variable de entorno
    (nunca con la clave escrita en el repositorio). En las pruebas: ClienteLLMFalso."""

    def __init__(self, cliente):
        self._cliente = cliente

    def completar(self, prompt):
        return self._cliente.generate(prompt)


class ConCacheLLM(ProveedorLLM):
    """DECORATOR: evita pagar dos veces por el mismo prompt."""

    def __init__(self, interno: ProveedorLLM):
        self._interno, self._cache = interno, {}

    def completar(self, prompt):
        if prompt not in self._cache:
            self._cache[prompt] = self._interno.completar(prompt)
        return self._cache[prompt]


# ---------- CHAIN OF RESPONSIBILITY: guardrails de salida ----------
class Guardrail(ABC):
    def __init__(self, siguiente=None):
        self._siguiente = siguiente

    def validar(self, texto: str) -> str:
        texto = self._aplicar(texto)
        return self._siguiente.validar(texto) if self._siguiente else texto

    @abstractmethod
    def _aplicar(self, texto: str) -> str: ...


class SinPrecios(Guardrail):
    def _aplicar(self, texto):
        if "S/" in texto:
            raise ValueError("Guardrail: la IA incluyo un precio")
        return texto


class LongitudMaxima(Guardrail):
    def __init__(self, maximo=280, siguiente=None):
        super().__init__(siguiente)
        self._maximo = maximo

    def _aplicar(self, texto):
        if len(texto) > self._maximo:
            raise ValueError("Guardrail: texto demasiado largo")
        return texto


class SinAfirmacionesProhibidas(Guardrail):
    PROHIBIDAS = ["garantizado", "seguro que"]

    def _aplicar(self, texto):
        for palabra in self.PROHIBIDAS:
            if palabra in texto.lower():
                raise ValueError("Guardrail: afirmacion no permitida")
        return texto


def cadena_por_defecto() -> Guardrail:
    return SinPrecios(LongitudMaxima(280, SinAfirmacionesProhibidas()))
