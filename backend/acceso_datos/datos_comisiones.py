"""Módulo para la gestión de datos de comisiones generadas por operaciones.

Este módulo se encarga de cargar y registrar las comisiones cobradas en las
transacciones del exchange. Cada comisión se guarda como un registro en un
archivo JSON, incluyendo detalles como el activo, la cantidad y su valor en USD.
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Optional

from backend.utils.utilidades_numericas import cuantizar_cripto, cuantizar_usd
import config

def cargar_comisiones(ruta_archivo: Optional[str] = None) -> list:
    """Carga el historial de comisiones desde un archivo JSON.

    Lee el archivo de comisiones. Si el archivo no existe, está vacío, corrupto
    o no contiene una lista, devuelve una lista vacía como fallback seguro.

    Args:
        ruta_archivo (Optional[str]): Ruta al archivo. Si es None, se usa la
                                     ruta de `config.COMISIONES_PATH`.

    Returns:
        list: Una lista de diccionarios, donde cada uno representa una comisión.
              Devuelve una lista vacía si el archivo no puede ser cargado o no
              contiene una lista.
    """
    ruta_efectiva = ruta_archivo or config.COMISIONES_PATH
    if not os.path.exists(ruta_efectiva) or os.path.getsize(ruta_efectiva) == 0:
        return []
    try:
        with open(ruta_efectiva, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Asegurarse de que siempre devolvemos una lista
            if isinstance(data, list):
                return data
            else:
                print(f"Advertencia: El archivo de comisiones '{ruta_efectiva}' no contiene una lista. Se devolverá una lista vacía.")
                return []
    except Exception as e:
        print(f"Advertencia: No se pudo leer o el archivo '{ruta_efectiva}' está corrupto. Error: {e}")
        return []

def registrar_comision(
    ticker_comision: str,
    cantidad_comision: Decimal,
    valor_usd_comision: Decimal,
    ruta_archivo: Optional[str] = None
):
    """Registra una nueva comisión y la persiste en el archivo JSON.

    Crea un nuevo registro de comisión, lo añade al principio de la lista
    existente y guarda la lista actualizada. Los valores Decimal se convierten
    a string con precisión estandarizada.

    Args:
        ticker_comision (str): Ticker del activo en el que se cobró la comisión.
        cantidad_comision (Decimal): Cantidad del activo cobrada.
        valor_usd_comision (Decimal): Valor equivalente en USD de la comisión.
        ruta_archivo (Optional[str]): Ruta al archivo. Si es None, se usa la
                                     ruta de `config.COMISIONES_PATH`.

    Side Effects:
        - Crea el directorio si no existe.
        - Lee y reescribe el archivo de comisiones completo.
    """
    ruta_efectiva = ruta_archivo or config.COMISIONES_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)
    comisiones = cargar_comisiones(ruta_archivo=ruta_efectiva)

    # Cuantizar valores para asegurar precisión y formato estándar.
    cantidad_comision_q = cuantizar_cripto(cantidad_comision)
    valor_usd_comision_q = cuantizar_usd(valor_usd_comision)

    nueva_comision = {
        "id": len(comisiones) + 1,
        "timestamp": datetime.now().isoformat(),
        "ticker": ticker_comision,
        "cantidad": str(cantidad_comision_q),
        "valor_usd": str(valor_usd_comision_q),
    }
    
    print(
        f"💰 COMISIÓN REGISTRADA: "
        f"{nueva_comision['cantidad']} {nueva_comision['ticker']} "
        f"(valor: ${nueva_comision['valor_usd']})"
    )

        # Insertar al principio para que las comisiones más recientes aparezcan primero.
    comisiones.insert(0, nueva_comision)

    try:
        with open(ruta_efectiva, "w", encoding="utf-8") as f:
            json.dump(comisiones, f, indent=4)
    except Exception as e:
        print(f"Error crítico: No se pudo escribir en el archivo de comisiones '{ruta_efectiva}'. Error: {e}")