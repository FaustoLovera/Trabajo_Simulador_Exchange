import json
import os
from datetime import datetime
from decimal import Decimal
from config import HISTORIAL_PATH


def cargar_historial():
    """
    Carga el historial de transacciones desde el archivo JSON.

    Lee el archivo especificado en `HISTORIAL_PATH`. Si el archivo no existe,
    está vacío o contiene JSON mal formado, devuelve una lista vacía para
    prevenir errores en la aplicación.

    Returns:
        list[dict]: Una lista de diccionarios, donde cada uno representa una
                    transacción guardada. Devuelve una lista vacía si la
                    carga falla.

    Example:
        >>> historial = cargar_historial()
        >>> print(historial)
        [{'id': 1, 'timestamp': '...', 'tipo': 'compra', ...}]
    """
    if not os.path.exists(HISTORIAL_PATH) or os.path.getsize(HISTORIAL_PATH) == 0:
        return []

    try:
        with open(HISTORIAL_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(
            f"Advertencia: No se pudo leer o el archivo '{HISTORIAL_PATH}' está corrupto."
        )
        return []


def guardar_en_historial(
    tipo_operacion: str,
    moneda_origen: str,
    cantidad_origen: Decimal,
    moneda_destino: str,
    cantidad_destino: Decimal,
    valor_usd: Decimal,
):
    """
    Guarda una nueva operación en el historial de transacciones.

    Carga el historial existente, crea un nuevo registro de operación y lo
    añade al principio de la lista. Finalmente, guarda la lista actualizada
    en el archivo JSON.

    Args:
        tipo_operacion (str): El tipo de operación (ej. "compra", "venta").
        moneda_origen (str): Ticker de la moneda de origen (ej. "USDT").
        cantidad_origen (Decimal): La cantidad de la moneda de origen.
        moneda_destino (str): Ticker de la moneda de destino (ej. "BTC").
        cantidad_destino (Decimal): La cantidad de la moneda de destino.
        valor_usd (Decimal): El valor total de la transacción en USD.

    Example:
        >>> guardar_en_historial(
                "compra", "USDT", Decimal("100"), "BTC", Decimal("0.0015"), Decimal("100")
            )
        # Esto añadirá una nueva entrada al archivo historial.json
    """
    # Asegura que el directorio del historial exista.
    os.makedirs(os.path.dirname(HISTORIAL_PATH), exist_ok=True)

    historial = cargar_historial()

    # Crea el diccionario para la nueva operación.
    # Las cantidades Decimal se convierten a string para preservar la precisión.
    operacion = {
        "id": len(historial) + 1,
        "timestamp": datetime.now().isoformat(),
        "tipo": tipo_operacion,
        "origen": {"ticker": moneda_origen, "cantidad": str(cantidad_origen)},
        "destino": {"ticker": moneda_destino, "cantidad": str(cantidad_destino)},
        "valor_usd": str(valor_usd.quantize(Decimal("0.01"))),
    }

    # Añade la nueva operación al principio de la lista para mostrarla primero.
    historial.insert(0, operacion)

    # Guarda la lista completa de nuevo en el archivo.
    with open(HISTORIAL_PATH, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4)
