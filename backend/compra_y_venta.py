from flask import request, redirect, url_for, render_template, flash
import json
import os

COTIZACIONES_PATH = os.path.join(os.getcwd(), 'datos', 'datos_cotizaciones.json')
BILLETERA_PATH = os.path.join(os.getcwd(), 'datos', 'billetera.json')

def cargar_datos_cotizaciones():
    try:
        with open(COTIZACIONES_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró el archivo de cotizaciones locales.")
        return []
    

def procesar_operacion_trading(formulario, datos_cotizaciones):
    ticker = formulario["ticker"]
    accion = formulario["accion"]
    monto = float(formulario["monto"])

    if accion == "comprar":
        return comprar_cripto(ticker, monto, datos_cotizaciones)
    elif accion == "vender":
        return vender_cripto(ticker, monto, datos_cotizaciones)
    else:
        return False, "❌ Acción inválida."

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
    criptos_sin_usdt = {}
    for clave, valor in billetera.items():
        if clave != "USDT":
            criptos_sin_usdt[clave] = valor

    estado = {
        "USDT": billetera.get("USDT"),
        "criptos": criptos_sin_usdt
    }
    return estado

def obtener_precio(ticker, datos_criptos):
    for cripto in datos_criptos:
        if cripto["ticker"].lower() == ticker.lower():
            return cripto["precio_usd"]
    return None

def comprar_cripto(ticker, monto_usd, datos_criptos):
    billetera = cargar_billetera()
    precio = obtener_precio(ticker, datos_criptos)

    if precio is None:
        return False, f"❌ No se encontró el ticker {ticker}"

    if monto_usd > billetera["USDT"]:
        return False, "❌ Saldo insuficiente"

    billetera["USDT"] -= monto_usd

    cantidad = monto_usd / precio
    billetera[ticker] = billetera.get(ticker, 0) + cantidad

    guardar_billetera(billetera)
    return True, f"✅ Compra exitosa: {cantidad:.6f} {ticker} por {monto_usd:.2f} USDT"


def vender_cripto(ticker, cantidad_a_vender, datos_criptos):
    billetera = cargar_billetera()
    precio = obtener_precio(ticker, datos_criptos)

    if precio is None:
        return False, f"❌ No se encontró el ticker {ticker}"

    cantidad_actual = billetera.get(ticker, 0)

    if cantidad_actual < cantidad_a_vender:
        return False, f"❌ No tenés suficiente {ticker} para vender (disponible: {cantidad_actual:.6f})"

    monto_usd = cantidad_a_vender * precio
    billetera["USDT"] += monto_usd
    billetera[ticker] -= cantidad_a_vender

    if billetera[ticker] <= 0:
        billetera.pop(ticker)

    guardar_billetera(billetera)
    return True, f"✅ Venta exitosa: {cantidad_a_vender:.6f} {ticker} por ${monto_usd:.2f}"

def vista_trading():
    criptos = cargar_datos_cotizaciones()
    estado = obtener_estado()

    if request.method == "POST":
        exito, mensaje = procesar_operacion_trading(request.form, criptos)
        flash(mensaje, "success" if exito else "danger")
        return redirect(url_for("trading"))

    return render_template("trading.html", criptos=criptos, estado=estado)