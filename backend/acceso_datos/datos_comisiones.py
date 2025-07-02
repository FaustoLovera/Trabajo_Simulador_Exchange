# backend/acceso_datos/datos_comisiones.py
### MODIFICADO ###

import json
import os
from datetime import datetime
from decimal import Decimal
from typing import Optional

from backend.utils.utilidades_numericas import cuantizar_cripto, cuantizar_usd
from config import COMISIONES_PATH

def cargar_comisiones(ruta_archivo: Optional[str] = None) -> list:
    """Carga el historial de comisiones desde el archivo JSON."""
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else COMISIONES_PATH
    if not os.path.exists(ruta_efectiva) or os.path.getsize(ruta_efectiva) == 0:
        return []
    try:
        with open(ruta_efectiva, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Advertencia: No se pudo leer o el archivo '{ruta_efectiva}' está corrupto.")
        return []

def registrar_comision(
    ticker_comision: str,
    cantidad_comision: Decimal,
    valor_usd_comision: Decimal,
    ruta_archivo: Optional[str] = None
):
    """
    Guarda un nuevo registro de comisión usando las utilidades de cuantización.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else COMISIONES_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)
    comisiones = cargar_comisiones(ruta_archivo=ruta_efectiva)

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

    comisiones.insert(0, nueva_comision)

    with open(ruta_efectiva, "w", encoding="utf-8") as f:
        json.dump(comisiones, f, indent=4)