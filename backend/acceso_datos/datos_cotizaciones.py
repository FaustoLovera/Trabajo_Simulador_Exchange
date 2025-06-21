import json
import os
from decimal import Decimal, InvalidOperation
from config import COTIZACIONES_PATH


def obtener_precio(ticker):
    """
    Obtiene el precio de un ticker específico desde el archivo de cotizaciones.
    Devuelve el precio como un objeto Decimal, o None si no se encuentra.
    """
    cotizaciones = cargar_datos_cotizaciones()
    ticker_lower = ticker.lower()

    for cripto in cotizaciones:
        if cripto.get("ticker", "").lower() == ticker_lower:
            # Aseguramos que devolvemos un Decimal válido
            try:
                return Decimal(str(cripto.get("precio_usd")))
            except (InvalidOperation, TypeError):
                return Decimal("0")  # Devuelve 0 si el precio es inválido

    return None  # Retorna None si el ticker no se encuentra en la lista


def cargar_datos_cotizaciones():
    """
    Función interna y segura para cargar todas las cotizaciones.
    Maneja archivos inexistentes o corruptos.
    """
    if not os.path.exists(COTIZACIONES_PATH) or os.path.getsize(COTIZACIONES_PATH) == 0:
        return []

    try:
        with open(COTIZACIONES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []
