"""
Módulo de Acceso a Datos para las Comisiones.

Este módulo se encarga de la persistencia de los registros de comisiones
cobrados por las operaciones de trading.
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from config import COMISIONES_PATH


def cargar_comisiones() -> list:
    """
    Carga el historial de comisiones desde el archivo JSON.

    Si el archivo no existe o está vacío, devuelve una lista vacía.
    
    Returns:
        list: Una lista de diccionarios, donde cada uno es un registro de comisión.
    """
    if not os.path.exists(COMISIONES_PATH) or os.path.getsize(COMISIONES_PATH) == 0:
        return []

    try:
        with open(COMISIONES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Advertencia: No se pudo leer o el archivo '{COMISIONES_PATH}' está corrupto.")
        return []


def registrar_comision(
    ticker_comision: str,
    cantidad_comision: Decimal,
    valor_usd_comision: Decimal
):
    """
    Guarda un nuevo registro de comisión en el archivo `comisiones.json`.

    Args:
        ticker_comision (str): El ticker de la moneda en la que se cobró la comisión (ej. "BTC").
        cantidad_comision (Decimal): La cantidad de la moneda cobrada como comisión.
        valor_usd_comision (Decimal): El valor equivalente en USD de la comisión cobrada.
    """
    # Asegura que el directorio exista antes de intentar escribir.
    os.makedirs(os.path.dirname(COMISIONES_PATH), exist_ok=True)

    comisiones = cargar_comisiones()

    # Prepara el nuevo registro de comisión.
    nueva_comision = {
        "id": len(comisiones) + 1,
        "timestamp": datetime.now().isoformat(),
        "ticker": ticker_comision,
        "cantidad": str(cantidad_comision.quantize(Decimal("0.00000001"))),
        "valor_usd": str(valor_usd_comision.quantize(Decimal("0.01"))),
    }

    # Imprime en la terminal para un feedback inmediato durante el desarrollo.
    print(
        f"💰 COMISIÓN REGISTRADA: "
        f"{nueva_comision['cantidad']} {nueva_comision['ticker']} "
        f"(valor: ${nueva_comision['valor_usd']})"
    )

    # Añade la nueva comisión al principio de la lista para verla primero.
    comisiones.insert(0, nueva_comision)

    # Guarda la lista completa de nuevo en el archivo.
    with open(COMISIONES_PATH, "w", encoding="utf-8") as f:
        json.dump(comisiones, f, indent=4)