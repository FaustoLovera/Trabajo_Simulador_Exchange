# backend/acceso_datos/datos_billetera.py
### MODIFICADO Y SIMPLIFICADO ###

import json
import os
from decimal import Decimal
from typing import Optional

from backend.utils.utilidades_numericas import a_decimal, cuantizar_cripto
from config import BILLETERA_PATH, BALANCE_INICIAL_USDT

def _crear_billetera_inicial() -> dict:
    """Crea el objeto de billetera inicial con la nueva estructura."""
    return {
        "USDT": {
            "nombre": "Tether",
            "saldos": {
                "disponible": a_decimal(BALANCE_INICIAL_USDT),
                "reservado": a_decimal("0")
            }
        }
    }

def cargar_billetera(ruta_archivo: Optional[str] = None) -> dict[str, dict]:
    """
    Carga la billetera de criptomonedas desde un archivo JSON.
    Si no se provee una ruta, usa la ruta por defecto de la configuración.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else BILLETERA_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)

    if not os.path.exists(ruta_efectiva) or os.path.getsize(ruta_efectiva) == 0:
        billetera_inicial = _crear_billetera_inicial()
        guardar_billetera(billetera_inicial, ruta_archivo=ruta_efectiva)
        return billetera_inicial

    try:
        with open(ruta_efectiva, "r", encoding="utf-8") as f:
            datos_cargados = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print(f"Advertencia: Archivo '{ruta_efectiva}' corrupto. Se reiniciará la billetera.")
        billetera_inicial = _crear_billetera_inicial()
        guardar_billetera(billetera_inicial, ruta_archivo=ruta_efectiva)
        return billetera_inicial

    billetera_final = {}
    for ticker, activo in datos_cargados.items():
        billetera_final[ticker] = {
            "nombre": activo.get("nombre", ticker),
            "saldos": {
                "disponible": a_decimal(activo["saldos"].get("disponible", "0")),
                "reservado": a_decimal(activo["saldos"].get("reservado", "0"))
            }
        }
    return billetera_final

def guardar_billetera(billetera: dict[str, dict], ruta_archivo: Optional[str] = None):
    """
    Guarda el estado actual de la billetera en un archivo JSON.
    Si no se provee una ruta, usa la ruta por defecto de la configuración.
    """
    ruta_efectiva = ruta_archivo if ruta_archivo is not None else BILLETERA_PATH
    os.makedirs(os.path.dirname(ruta_efectiva), exist_ok=True)

    datos_para_json = {}
    for ticker, activo in billetera.items():
        saldos = activo.get("saldos", {})
        
        saldo_disponible = saldos.get("disponible", a_decimal(0))
        saldo_reservado = saldos.get("reservado", a_decimal(0))
        
        saldo_disponible_q = cuantizar_cripto(saldo_disponible)
        saldo_reservado_q = cuantizar_cripto(saldo_reservado)
        
        str_disponible = "0.00000000" if saldo_disponible_q.is_zero() else str(saldo_disponible_q)
        str_reservado = "0.00000000" if saldo_reservado_q.is_zero() else str(saldo_reservado_q)
        
        datos_para_json[ticker] = {
            "nombre": activo.get("nombre", ticker),
            "saldos": {
                "disponible": str_disponible,
                "reservado": str_reservado,
            }
        }

    with open(ruta_efectiva, "w", encoding="utf-8") as f:
        json.dump(datos_para_json, f, indent=4)