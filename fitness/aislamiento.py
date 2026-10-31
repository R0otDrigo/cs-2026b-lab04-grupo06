"""Prototipo de aislamiento entre operadores (ADR-008): el repositorio NO permite consultar sin operador."""
import sqlite3


class RepositorioViajes:
    def __init__(self, conexion):
        self._c = conexion
        self._c.execute("CREATE TABLE IF NOT EXISTS viaje (placa TEXT, operador_id TEXT)")

    def agregar(self, operador_id, placa):
        self._c.execute("INSERT INTO viaje VALUES (?, ?)", (placa, operador_id))

    def listar(self, operador_id):
        if not operador_id:
            raise ValueError("Se requiere el operador para consultar viajes")
        return self._c.execute("SELECT placa, operador_id FROM viaje WHERE operador_id = ?",
                               (operador_id,)).fetchall()


def base_de_prueba(buses_por_operador=600):
    repo = RepositorioViajes(sqlite3.connect(":memory:"))
    for operador in ("OPERADOR_A", "OPERADOR_B"):
        for i in range(buses_por_operador):
            repo.agregar(operador, f"{operador[-1]}-{i:04d}")
    return repo
