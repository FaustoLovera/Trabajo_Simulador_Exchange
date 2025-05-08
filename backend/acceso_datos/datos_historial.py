import json
from config import HISTORIAL_PATH
from decimal import Decimal
import os

def cargar_historial():
    try:
        with open(HISTORIAL_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []



def guardar_en_historial(tipo, ticker, cantidad, monto_usdt, precio_unitario):
    crear_operacion = lambda id, tipo, ticker, cantidad, monto_usdt, precio_unitario: {
        "id": id,
        "tipo": tipo,
        "ticker": ticker,
        "cantidad": cantidad,
        "monto_usdt": monto_usdt,
        "precio_unitario": precio_unitario,
    }

    os.makedirs(os.path.dirname(HISTORIAL_PATH), exist_ok=True)

    if os.path.exists(HISTORIAL_PATH):
        with open(HISTORIAL_PATH, "r") as f:
            historial = json.load(f)
        for operacion in historial:
            operacion["cantidad"] = Decimal(operacion["cantidad"])
            operacion["monto_usdt"] = Decimal(operacion["monto_usdt"])
            operacion["precio_unitario"] = Decimal(operacion["precio_unitario"])
    else:
        historial = []

    nuevo_id = len(historial) + 1
    cantidad = cantidad.quantize(Decimal("0.00000001"))

    operacion = crear_operacion(
        nuevo_id, tipo, ticker, cantidad, monto_usdt, precio_unitario
    )
    historial.insert(0, operacion)

    with open(HISTORIAL_PATH, "w") as f:
        json.dump(historial, f, indent=4, default=lambda o: str(o) if isinstance(o, Decimal) else o)