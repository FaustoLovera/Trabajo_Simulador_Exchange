# backend/acceso_datos/datos_historial.py
### MODIFICADO ###

import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Optional

from backend.utils.utilidades_numericas import cuantizar_cripto, cuantizar_usd
from config import HISTORIAL_PATH

def cargar_historial(ruta_archivo: Optional[str] = None) -> list:
    """
    Carga el historial de transacciones desde el archivo JSON.
    Si no se provee una ruta, usa la ruta por defecto de la configuración.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else HISTORIAL_PATH
    if not os.path.exists(ruta_efectiva) or os.path.getsize(ruta_efectiva) == 0:
        return []

    try:
        with open(ruta_efectiva, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(
            f"Advertencia: No se pudo leer o el archivo '{ruta_efectiva}' está corrupto."
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
    """
    Guarda una nueva operación en el historial de transacciones.
    Si no se provee una ruta, usa la ruta por defecto de la configuración.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else HISTORIAL_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)
    historial = cargar_historial(ruta_archivo=ruta_efectiva)

    cantidad_origen_q = cuantizar_cripto(cantidad_origen)
    cantidad_destino_q = cuantizar_cripto(cantidad_destino)
    valor_usd_q = cuantizar_usd(valor_usd)

    operacion = {
        "id": len(historial) + 1,
        "timestamp": datetime.now().isoformat(),
        "tipo": tipo_operacion,
        "origen": {"ticker": moneda_origen, "cantidad": str(cantidad_origen_q)},
        "destino": {"ticker": moneda_destino, "cantidad": str(cantidad_destino_q)},
        "valor_usd": str(valor_usd_q),
    }

    historial.insert(0, operacion)

    with open(ruta_efectiva, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4)