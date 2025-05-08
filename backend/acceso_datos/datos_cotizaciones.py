import json
from config import COTIZACIONES_PATH
from decimal import Decimal

def obtener_precio(ticker):
    datos = []
    try:
        with open(COTIZACIONES_PATH, "r") as f:
            datos = json.load(f)
    except FileNotFoundError:
        return None

    for cripto in datos:
        if cripto["ticker"].lower() == ticker.lower():
            return Decimal(str(cripto["precio_usd"]))

    return None