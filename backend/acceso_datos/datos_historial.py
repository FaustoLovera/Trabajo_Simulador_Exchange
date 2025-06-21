import json
import os
from datetime import datetime
from decimal import Decimal
from config import HISTORIAL_PATH


def cargar_historial():
    """
    Carga el historial de transacciones desde el archivo JSON.
    Si el archivo no existe, está vacío o corrupto, devuelve una lista vacía.
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
    tipo_operacion,
    moneda_origen,
    cantidad_origen,
    moneda_destino,
    cantidad_destino,
    valor_usd,
):
    """
    Guarda una nueva operación en el historial de transacciones.
    """
    # Asegurarse de que el directorio de datos exista
    os.makedirs(os.path.dirname(HISTORIAL_PATH), exist_ok=True)

    historial = cargar_historial()

    # Crear el diccionario para la nueva operación
    operacion = {
        "id": len(historial) + 1,
        "timestamp": datetime.now().isoformat(),
        "tipo": tipo_operacion,
        "origen": {"ticker": moneda_origen, "cantidad": str(cantidad_origen)},
        "destino": {"ticker": moneda_destino, "cantidad": str(cantidad_destino)},
        "valor_usd": str(valor_usd.quantize(Decimal("0.01"))),
    }

    # Añadir la nueva operación al principio de la lista
    historial.insert(0, operacion)

    # Escribir la lista completa de nuevo en el archivo
    with open(HISTORIAL_PATH, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4)
