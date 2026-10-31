"""Prototipo de autenticacion de dispositivos GPS (ADR-008): firma HMAC-SHA256 con marca de tiempo."""
import hashlib
import hmac

VENTANA_S = 60


def firmar(secreto: bytes, bus: str, lat: float, lon: float, ts: int) -> str:
    mensaje = f"{bus}|{lat}|{lon}|{ts}".encode()
    return hmac.new(secreto, mensaje, hashlib.sha256).hexdigest()


def verificar(secreto: bytes, bus, lat, lon, ts, firma: str, ahora: int) -> bool:
    if abs(ahora - ts) > VENTANA_S:
        return False  # mensaje viejo: evita reenvios (replay)
    return hmac.compare_digest(firmar(secreto, bus, lat, lon, ts), firma)
