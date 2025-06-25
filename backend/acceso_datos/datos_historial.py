# backend/acceso_datos/datos_historial.py
### MODIFICADO ###

import json
import os
from datetime import datetime
from decimal import Decimal

# Importamos las nuevas utilidades numéricas
from backend.utils.utilidades_numericas import cuantizar_cripto, cuantizar_usd
from config import HISTORIAL_PATH


def cargar_historial():
    """
    Carga el historial de transacciones desde el archivo JSON.
    (Sin cambios en la carga, la conversión a Decimal se hace en la capa de servicios).
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

    Usa las utilidades de cuantización para asegurar la precisión correcta
    antes de guardar los datos en el archivo JSON.
    """
    os.makedirs(os.path.dirname(HISTORIAL_PATH), exist_ok=True)
    historial = cargar_historial()

    # ### ANTES: usaba .quantize() con valores mágicos.
    # ### DESPUÉS: usamos las utilidades centralizadas.
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

    with open(HISTORIAL_PATH, "w", encoding="utf-8") as f:
        json.dump(historial, f, indent=4)