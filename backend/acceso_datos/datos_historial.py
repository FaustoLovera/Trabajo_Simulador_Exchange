"""Módulo para la persistencia del historial de transacciones.

Este componente gestiona la lectura y escritura del historial de operaciones
en un archivo JSON. Cada operación se guarda como un registro inmutable.

El sistema está diseñado para ser robusto, devolviendo una lista vacía si
el archivo de historial no existe o está corrupto, permitiendo que la
aplicación continúe funcionando.
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from backend.utils.utilidades_numericas import cuantizar_cripto, cuantizar_usd
import config

def cargar_historial(ruta_archivo: Optional[str] = None) -> List[Dict[str, Any]]:
    """Carga el historial de transacciones desde un archivo JSON.

    Es una operación de solo lectura y "a prueba de fallos": si el archivo
    no existe, está vacío o corrupto, devuelve una lista vacía para no
    interrumpir la ejecución de la aplicación.

    Args:
        ruta_archivo (Optional[str]): Ruta al archivo. Si es None, se usa la
                                     ruta por defecto de la configuración.

    Returns:
        List[Dict[str, Any]]: Una lista de registros de transacciones.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else config.HISTORIAL_PATH
    if not os.path.exists(ruta_efectiva) or os.path.getsize(ruta_efectiva) == 0:
        return []

    try:
        with open(ruta_efectiva, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(
            f"Advertencia: No se pudo leer o el archivo '{ruta_efectiva}' está corrupto. Error: {e}"
        )
        return []

def guardar_en_historial(
    tipo_operacion: str,
    moneda_origen: str,
    cantidad_origen: Decimal,
    moneda_destino: str,
    cantidad_destino: Decimal,
    valor_usd: Decimal,
    ruta_archivo: Optional[str] = None,
):
    """Añade un nuevo registro de transacción al historial.

    Implementa un ciclo de "leer-modificar-escribir": carga el historial
    completo, añade la nueva transacción al principio de la lista y
    sobrescribe el archivo. Este enfoque mantiene las operaciones más
    recientes primero.

    Args:
        tipo_operacion (str): Tipo de la operación (ej. 'COMPRA').
        moneda_origen (str): Ticker de la moneda entregada.
        cantidad_origen (Decimal): Cantidad de la moneda entregada.
        moneda_destino (str): Ticker de la moneda recibida.
        cantidad_destino (Decimal): Cantidad de la moneda recibida.
        valor_usd (Decimal): Valor total de la transacción en USD.
        ruta_archivo (Optional[str]): Ruta al archivo de historial.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else config.HISTORIAL_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)
    historial = cargar_historial(ruta_archivo=ruta_efectiva)

    # Cuantizar valores para asegurar precisión y formato estándar.
    cantidad_origen_q = cuantizar_cripto(cantidad_origen)
    cantidad_destino_q = cuantizar_cripto(cantidad_destino)
    valor_usd_q = cuantizar_usd(valor_usd)

    # Creación del nuevo registro de transacción.
    operacion = {
        "id": len(historial) + 1,
        "timestamp": datetime.now().isoformat(),
        "tipo": tipo_operacion,
        "origen": {"ticker": moneda_origen, "cantidad": str(cantidad_origen_q)},
        "destino": {"ticker": moneda_destino, "cantidad": str(cantidad_destino_q)},
        "valor_usd": str(valor_usd_q),
    }

    # Se inserta la nueva operación al principio de la lista.
    # Esto asegura que el historial se muestre en orden cronológico descendente.
    historial.insert(0, operacion)

    try:
        with open(ruta_efectiva, "w", encoding="utf-8") as f:
            json.dump(historial, f, indent=4)
    except Exception as e:
        # En un entorno de producción, esto debería ser manejado por un sistema de logging.
        print(
            f"Error Crítico: No se pudo guardar el archivo de historial en '{ruta_efectiva}'. Error: {e}"
        )