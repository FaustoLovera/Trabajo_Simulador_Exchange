from flask import request, redirect, url_for, render_template, flash
import json
import os

COTIZACIONES_PATH = "./datos/datos_cotizaciones.json"
BILLETERA_PATH = "./datos/billetera.json"

def cargar_datos_cotizaciones():
    try:
        with open(COTIZACIONES_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró el archivo de cotizaciones locales.")
        return []

def obtener_precio(ticker):
    try:
        with open(COTIZACIONES_PATH, 'r') as f:
            datos_criptos = json.load(f)
    except FileNotFoundError:
        return None

    for cripto in datos_criptos:
        if cripto["ticker"].lower() == ticker.lower():
            return cripto["precio_usd"]
    return None

def procesar_operacion_trading(formulario):
    ticker = formulario["ticker"]
    accion = formulario["accion"]
    monto = float(formulario["monto"])

    if accion == "comprar":
        return comprar_cripto(ticker, monto)
    elif accion == "vender":
        return vender_cripto(ticker, monto)
    else:
        return False, "❌ Acción inválida."

def cargar_billetera():
    try:
        with open(BILLETERA_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"USDT": 0}

def guardar_billetera(billetera):
    with open(BILLETERA_PATH, 'w') as f:
        json.dump(billetera, f, indent=4)

obtener_estado = lambda: cargar_billetera()


def comprar_cripto(ticker, monto_usd):
    billetera = cargar_billetera()
    precio = obtener_precio(ticker)

    if precio is None:
        return False, f"❌ No se encontró el ticker {ticker}"

    if monto_usd > billetera["USDT"]:
        return False, "❌ Saldo insuficiente"

    billetera["USDT"] -= monto_usd

    cantidad = monto_usd / precio
    if ticker in billetera:
        billetera[ticker] += cantidad
    else:
        billetera[ticker] = cantidad

    guardar_billetera(billetera)
    guardar_en_historial("compra", ticker, cantidad, monto_usd, precio)
    return True, f"✅ Compra exitosa: {cantidad:.6f} {ticker} por {monto_usd:.2f} USDT"

def vender_cripto(ticker, cantidad_a_vender):
    billetera = cargar_billetera()
    precio = obtener_precio(ticker)

    if precio is None:
        return False, f"❌ No se encontró el ticker {ticker}"

    if ticker in billetera:
        cantidad_actual = billetera[ticker]
    else:
        cantidad_actual = 0

    if cantidad_actual < cantidad_a_vender:
        return False, f"❌ No tenés suficiente {ticker} para vender (disponible: {cantidad_actual:.6f})"

    monto_usd = cantidad_a_vender * precio
    if "USDT" in billetera:
        billetera["USDT"] += monto_usd
    else:
        billetera["USDT"] = monto_usd
    billetera[ticker] -= cantidad_a_vender

    if billetera[ticker] <= 0:
        billetera.pop(ticker)

    guardar_billetera(billetera)
    guardar_en_historial("venta", ticker, cantidad_a_vender, monto_usd, precio)
    return True, f"✅ Venta exitosa: {cantidad_a_vender:.6f} {ticker} por ${monto_usd:.2f}"

def trading():
    criptos = cargar_datos_cotizaciones()   # Esto devuelve una lista de diccionarios desde el json de cotizaciones
    estado = obtener_estado()               # Esto devuelve un diccionario del valor de USDT y demás criptos que estén en billetera

    print(estado)
    if request.method == "POST":
        exito, mensaje = procesar_operacion_trading(request.form) # Es lo que trae Flask desde el formulario de trading.html. ALGO ASI: request.form = { "ticker": "BTC", "monto": "5000", "accion": "comprar"}
        flash(mensaje, "success" if exito else "danger")
        return redirect(url_for("trading"))

    return render_template("trading.html", criptos=criptos, estado=estado)

HISTORIAL_PATH = "./datos/historial_operaciones.json"

def guardar_en_historial(tipo, ticker, cantidad, monto_usdt, precio_unitario):
    operacion = {
        "tipo": tipo,
        "ticker": ticker,
        "cantidad": cantidad,
        "monto_usdt": monto_usdt,
        "precio_unitario": precio_unitario
    }

    # Leer historial existente o iniciar una lista nueva
    if os.path.exists(HISTORIAL_PATH):
        with open(HISTORIAL_PATH, "r") as f:
            historial = json.load(f)
    else:
        historial = []

    historial.append(operacion)

    # Guardar el historial actualizado
    with open(HISTORIAL_PATH, "w") as f:
        json.dump(historial, f, indent=4)
