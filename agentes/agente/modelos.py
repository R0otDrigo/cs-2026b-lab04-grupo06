"""El 'cerebro' del agente es intercambiable (patrón Strategy del Lab 07).

Protocolo: el modelo recibe el historial y devuelve un JSON con
  {"pensamiento": "...", "accion": "<herramienta>", "args": {...}}   o
  {"pensamiento": "...", "final": "<respuesta para el usuario>"}
"""
import json, os

PROTOCOLO = (
    "PROTOCOLO: responde SOLO con un objeto JSON en UNA línea, sin texto adicional ni bloques de código.\n"
    'Para usar una herramienta: {"pensamiento": "...", "accion": "<herramienta>", "args": {...}}\n'
    'Para terminar: {"pensamiento": "...", "final": "<respuesta para el usuario>"}\n'
    "Solo puedes usar las herramientas del catálogo. Cada observación te llega en el siguiente mensaje."
)


class ModeloGrabado:
    """Reproduce decisiones grabadas de un asistente de IA (trayectoria JSON).
    Las herramientas se ejecutan de verdad; solo las decisiones vienen de la grabación."""
    def __init__(self, archivo):
        with open(archivo, encoding="utf-8") as f:
            self._decisiones = json.load(f)
        self._i = 0

    def decidir(self, historial: list) -> dict:
        d = self._decisiones[self._i]
        self._i += 1
        return d


class ModeloAnthropic:
    """Proveedor real (opcional). Requiere ANTHROPIC_API_KEY en una variable de entorno y el paquete anthropic."""
    def __init__(self, modelo="claude-sonnet-4-5", sistema=PROTOCOLO):
        import anthropic
        self._cliente, self._modelo, self._sistema = anthropic.Anthropic(), modelo, sistema

    def decidir(self, historial: list) -> dict:
        r = self._cliente.messages.create(model=self._modelo, max_tokens=1024, system=self._sistema,
                                          messages=historial, temperature=0)
        try:
            return json.loads(r.content[0].text)
        except json.JSONDecodeError:
            return r.content[0].text                     # el contrato lo rechaza y vuelve como observación


class ModeloInteractivo:
    """Sin clave de API: el estudiante copia el contexto a su asistente de IA (Claude.ai, ChatGPT,
    Gemini, Copilot Chat), pega aquí la respuesta JSON y la decisión se graba para reproducirla.

    Cambios respecto del framework original:
    - El orquestador agrega el PROTOCOLO al objetivo (antes el asistente no sabía el formato).
    - Si lo pegado no es JSON, no se cae: se graba tal cual y el contrato lo rechaza (guía, E2 paso 3).
    """
    def __init__(self, grabar_en, entrada=input):
        self._archivo, self._decisiones, self._entrada = grabar_en, [], entrada

    def decidir(self, historial: list):
        print("\n===== COPIE ESTO EN SU ASISTENTE DE IA =====")
        print(historial[0]["content"] if len(historial) == 1 else historial[-1]["content"])
        print("===== PEGUE LA RESPUESTA JSON (una línea) =====")
        texto = self._entrada("> ").strip()
        try:
            d = json.loads(texto)
        except json.JSONDecodeError:
            d = texto
        self._decisiones.append(d)
        os.makedirs(os.path.dirname(self._archivo) or ".", exist_ok=True)
        with open(self._archivo, "w", encoding="utf-8") as f:
            json.dump(self._decisiones, f, ensure_ascii=False, indent=1)
        return d
