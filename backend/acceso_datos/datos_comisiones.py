# backend/acceso_datos/datos_comisiones.py
### MODIFICADO ###

import json
import os
from datetime import datetime
from decimal import Decimal

# Importamos las nuevas utilidades numéricas
from backend.utils.utilidades_numericas import cuantizar_cripto, cuantizar_usd
from config import COMISIONES_PATH

def cargar_comisiones() -> list:
    """Carga el historial de comisiones desde el archivo JSON."""
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
    Guarda un nuevo registro de comisión usando las utilidades de cuantización.
    """
    os.makedirs(os.path.dirname(COMISIONES_PATH), exist_ok=True)
    comisiones = cargar_comisiones()

    # ### ANTES: usaba .quantize() con valores mágicos.
    # ### DESPUÉS: usamos las utilidades centralizadas.
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

    with open(COMISIONES_PATH, "w", encoding="utf-8") as f:
        json.dump(comisiones, f, indent=4)