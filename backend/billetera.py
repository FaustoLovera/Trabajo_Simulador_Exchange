import json
import os

HISTORIAL_PATH = "./datos/historial_operaciones.json"
BILLETERA_PATH = "./datos/billetera.json"
COTIZACIONES_PATH = "./datos/datos_cotizaciones.json"

def obtener_precios():
    with open(COTIZACIONES_PATH, "r") as f:
        datos = json.load(f)
    return {cripto["ticker"]: cripto["precio_usd"] for cripto in datos}

def cargar_historial():
    try:
        with open(HISTORIAL_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def cargar_datos_billetera():
    with open(BILLETERA_PATH, "r") as f:
        return json.load(f)

def estado_actual_completo():
    billetera = cargar_datos_billetera()
    precios = obtener_precios()
    historial = cargar_historial()

    detalle = []
    total_usdt = 0

    # Calcular valores y ganancias por cripto
    for ticker, cantidad_actual in billetera.items():
        if cantidad_actual < 0.000001:
            continue

        precio_actual = precios.get(ticker, 0)
        valor_usdt = cantidad_actual * precio_actual

        # Calcular monto invertido (solo compras)
        cantidad_comprada = 0
        total_invertido = 0
        for op in historial:
            if op["ticker"] == ticker and op["tipo"] == "compra":
                cantidad_comprada += op["cantidad"]
                total_invertido += op["monto_usdt"]

        precio_promedio = total_invertido / cantidad_comprada if cantidad_comprada > 0 else 0
        invertido_actual = cantidad_actual * precio_promedio
        ganancia = valor_usdt - invertido_actual
        porcentaje_ganancia = ((ganancia / invertido_actual) * 100) if invertido_actual != 0 else 0

        total_usdt += valor_usdt

        detalle.append({
            "ticker": ticker,
            "cantidad": cantidad_actual,
            "valor_usdt": valor_usdt,
            "precio_actual": precio_actual,
            "precio_promedio": precio_promedio,
            "invertido": invertido_actual,
            "ganancia_perdida": ganancia,
            "porcentaje_ganancia": porcentaje_ganancia
        })

    # Calcular porcentaje de participación
    for d in detalle:
        d["porcentaje"] = (d["valor_usdt"] / total_usdt) * 100 if total_usdt > 0 else 0

    return detalle
