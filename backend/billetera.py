
import json
import os

def cargar_datos_billetera():
    ruta_archivo = os.path.join("data", "billetera.json")
    with open(ruta_archivo, "r") as archivo:
        datos = json.load(archivo)
    return datos

def estado_actual_completo():
    with open("./datos/billetera.json", "r") as f:
        data = json.load(f)

    precios = obtener_precios()
    data = {k: v for k, v in data.items() if v >= 0.000001}

    detalle = []
    total_usdt = 0

    # Primero, calcular el total en USDT
    for moneda, cantidad in data.items():
        precio_usdt = precios.get(moneda, 0)
        valor_en_usdt = cantidad * precio_usdt
        total_usdt += valor_en_usdt

    # Ahora armar la lista con porcentaje incluido
    for moneda, cantidad in data.items():
        precio_usdt = precios.get(moneda, 0)
        valor_en_usdt = cantidad * precio_usdt
        porcentaje = (valor_en_usdt / total_usdt) * 100 if total_usdt > 0 else 0

        detalle.append({
            "ticker": moneda,
            "cantidad": cantidad,
            "valor_usdt": valor_en_usdt,
            "porcentaje": porcentaje,
            "precio_usd": precio_usdt
        })

    return detalle



def obtener_precios():
    with open("./datos/datos_cotizaciones.json", "r") as f:
        datos = json.load(f)

    precios = {}
    for cripto in datos:
        ticker = cripto.get("ticker")
        precio = cripto.get("precio_usd")
        if ticker and precio:
            precios[ticker] = precio
    return precios


