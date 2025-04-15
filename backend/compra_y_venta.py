import os
import json
from api_cotizaciones import obtener_datos_criptos_coingecko

BILLETERA_PATH = os.path.join(os.getcwd(), 'datos', 'billetera.json')

def cargar_billetera():
    try:
        with open(BILLETERA_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"saldo_usd": "ERROR"}

def guardar_billetera(billetera):
    with open(BILLETERA_PATH, 'w') as f:
        json.dump(billetera, f, indent=4)

def obtener_estado():
    billetera = cargar_billetera()
    estado = {
        "saldo_usd": billetera.get("saldo_usd"),
        "criptos": {k: v for k, v in billetera.items() if k != "saldo_usd"}  # Eliminar "saldo_usd" de las criptos
    }
    return estado

def obtener_precio(ticker, datos_criptos):
    """Obtiene el precio de una criptomoneda a partir de la lista de datos recibidos de la API"""
    for cripto in datos_criptos:
        if cripto["ticker"].lower() == ticker.lower():  # Se usa .lower() para hacer una comparación insensible al caso
            return cripto["precio_usd"]
    return None

def comprar_cripto(ticker, monto_usd):
    billetera = cargar_billetera()
    datos_criptos = obtener_datos_criptos_coingecko()

    precio = obtener_precio(ticker, datos_criptos)
    if precio is None:
        return False, f"❌ No se encontró el ticker {ticker}"

    if monto_usd > billetera["saldo_usd"]:
        return False, "❌ Saldo insuficiente"

    cantidad = monto_usd / precio
    billetera["saldo_usd"] -= monto_usd
    billetera[ticker] = billetera.get(ticker, 0) + cantidad

    guardar_billetera(billetera)
    return True, f"✅ Compra exitosa: {cantidad:.6f} {ticker} por ${monto_usd:.2f}"


def vender_cripto(ticker, cantidad_a_vender):
    billetera = cargar_billetera()
    datos_criptos = obtener_datos_criptos_coingecko()

    precio = obtener_precio(ticker, datos_criptos)
    if precio is None:
        return False, f"❌ No se encontró el ticker {ticker}"

    cantidad_actual = billetera.get(ticker, 0)

    if cantidad_actual < cantidad_a_vender:
        return False, f"❌ No tenés suficiente {ticker} para vender (disponible: {cantidad_actual:.6f})"

    monto_usd = cantidad_a_vender * precio
    billetera["saldo_usd"] += monto_usd
    billetera[ticker] -= cantidad_a_vender

    if billetera[ticker] <= 0:
        billetera.pop(ticker)

    guardar_billetera(billetera)
    return True, f"✅ Venta exitosa: {cantidad_a_vender:.6f} {ticker} por ${monto_usd:.2f}"
