"""VERSION ANTES (ingenua): consultar_eta() hace todo en un solo metodo."""
from rutasit.externos import GpsOperadorA, GpsOperadorB, MapasOSM, ClienteLLMFalso


class Viaje:
    def __init__(self, id, placa, operador, estado="PROGRAMADO"):
        self.id, self.placa, self.operador, self.estado = id, placa, operador, estado
        self.posiciones = []


class Estimacion:
    def __init__(self, minutos, disponible):
        self.minutos, self.disponible = minutos, disponible


class ServicioEta:
    def __init__(self, gps_a=None, gps_b=None, mapas=None, llm=None):
        self.gps_a = gps_a or GpsOperadorA()
        self.gps_b = gps_b or GpsOperadorB()
        self.mapas = mapas or MapasOSM()
        self.llm = llm or ClienteLLMFalso()
        self.eventos = []
        self.cache = {}

    def consultar_eta(self, viaje, paradero, algoritmo="MAPAS"):
        if viaje.estado != "EN_RUTA":
            if viaje.estado == "FINALIZADO":
                raise ValueError("El viaje ya finalizo")
            elif viaje.estado == "PROGRAMADO":
                raise ValueError("El viaje aun no inicia")
            else:
                raise ValueError("Estado no valido")
        # 1) leer la posicion segun el operador (con reintentos duplicados)
        pos = None
        if viaje.operador == "A":
            for intento in range(3):
                try:
                    r = self.gps_a.leer_posicion(viaje.placa)
                    pos = (r["lat"], r["lon"], r["vel_kmh"])
                    break
                except TimeoutError:
                    if intento == 2:
                        pos = None
        elif viaje.operador == "B":
            for intento in range(3):
                try:
                    la, lo, v, cod = self.gps_b.get_fix(viaje.placa)
                    if cod == 200:
                        pos = (la / 1e6, lo / 1e6, v * 3.6)
                    break
                except TimeoutError:
                    if intento == 2:
                        pos = None
        else:
            raise ValueError(f"Operador GPS no soportado: {viaje.operador}")
        if pos is None:
            self.eventos.append(f"alerta:{viaje.id}:sin senal")
            return Estimacion(0, False)
        viaje.posiciones.append(pos)
        # 2) calcular el ETA segun el algoritmo
        if algoritmo == "MAPAS":
            clave = (round(pos[0], 3), round(pos[1], 3), paradero)
            if clave in self.cache:
                minutos = self.cache[clave]
            else:
                minutos = None
                for intento in range(3):
                    try:
                        minutos = round(self.mapas.route_seconds(pos, paradero) / 60)
                        break
                    except TimeoutError:
                        if intento == 2:
                            minutos = None
                if minutos is None:
                    minutos = round(1.0 * 60 / max(pos[2], 5.0))
                else:
                    self.cache[clave] = minutos
        elif algoritmo == "VELOCIDAD":
            minutos = round(1.0 * 60 / max(pos[2], 5.0))
        else:
            raise ValueError(f"Algoritmo de ETA no soportado: {algoritmo}")
        # 3) avisar a los interesados a mano
        self.eventos.append(f"pasajero:{paradero}:llega en {minutos} min")
        if minutos > 20:
            self.eventos.append(f"alerta:{viaje.id}:retraso")
        return Estimacion(minutos, True)

    def sugerir_explicacion_retraso(self, eventos):
        prompt = "Explica el retraso: " + "; ".join(eventos)
        texto = self.llm.generate(prompt)
        if "S/" in texto:
            raise ValueError("Guardrail: la IA incluyo un precio")
        if len(texto) > 280:
            raise ValueError("Guardrail: texto demasiado largo")
        if "garantizado" in texto.lower() or "seguro que" in texto.lower():
            raise ValueError("Guardrail: afirmacion no permitida")
        return texto
