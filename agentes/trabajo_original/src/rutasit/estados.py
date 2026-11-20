"""Ciclo de vida del Viaje: patron State (maquina de estados del Lab 05)."""


class EstadoViaje:
    nombre = "?"

    def _prohibido(self, accion):
        raise ValueError(f"No se puede {accion} un viaje {self.nombre}")

    def iniciar(self, viaje): self._prohibido("iniciar")
    def marcar_desviado(self, viaje): self._prohibido("marcar desviado")
    def marcar_detenido(self, viaje): self._prohibido("marcar detenido")
    def reanudar(self, viaje): self._prohibido("reanudar")
    def finalizar(self, viaje): self._prohibido("finalizar")

    def verificar_eta(self, viaje):
        raise ValueError("Estado no valido")


class Programado(EstadoViaje):
    nombre = "PROGRAMADO"

    def iniciar(self, viaje): viaje.cambiar_a(EnRuta())
    def verificar_eta(self, viaje): raise ValueError("El viaje aun no inicia")


class EnRuta(EstadoViaje):
    nombre = "EN_RUTA"

    def marcar_desviado(self, viaje): viaje.cambiar_a(Desviado())
    def marcar_detenido(self, viaje): viaje.cambiar_a(Detenido())
    def finalizar(self, viaje): viaje.cambiar_a(Finalizado())
    def verificar_eta(self, viaje): return None


class Desviado(EstadoViaje):
    nombre = "DESVIADO"

    def reanudar(self, viaje): viaje.cambiar_a(EnRuta())
    def finalizar(self, viaje): viaje.cambiar_a(Finalizado())


class Detenido(EstadoViaje):
    nombre = "DETENIDO"

    def reanudar(self, viaje): viaje.cambiar_a(EnRuta())
    def finalizar(self, viaje): viaje.cambiar_a(Finalizado())


class Finalizado(EstadoViaje):
    nombre = "FINALIZADO"

    def verificar_eta(self, viaje): raise ValueError("El viaje ya finalizo")


ESTADOS = {e.nombre: e for e in (Programado, EnRuta, Desviado, Detenido, Finalizado)}
