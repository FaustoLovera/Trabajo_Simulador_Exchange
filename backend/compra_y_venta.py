from flask import request, redirect, url_for, render_template, flash
import json
import os

COTIZACIONES_PATH = "./datos/datos_cotizaciones.json"
BILLETERA_PATH = "./datos/billetera.json"
HISTORIAL_PATH = "./datos/historial_operaciones.json"


def cargar_datos_cotizaciones():
    try:
        with open(COTIZACIONES_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró el archivo de cotizaciones locales.")
        return []


def obtener_precio(ticker):
    try:
        with open(COTIZACIONES_PATH, "r") as f:
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
    # Asegurar que el directorio exista
    os.makedirs(os.path.dirname(BILLETERA_PATH), exist_ok=True)

    if not os.path.exists(BILLETERA_PATH):
        billetera_inicial = {"USDT": 100000}
        with open(BILLETERA_PATH, "w") as f:
            json.dump(billetera_inicial, f, indent=4)
        return billetera_inicial

    with open(BILLETERA_PATH, "r") as f:
        return json.load(f)


def guardar_billetera(billetera):
    with open(BILLETERA_PATH, "w") as f:
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
        return (
            False,
            f"❌ No tenés suficiente {ticker} para vender (disponible: {cantidad_actual:.6f})",
        )

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
    return (
        True,
        f"✅ Venta exitosa: {cantidad_a_vender:.6f} {ticker} por ${monto_usd:.2f}",
    )


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

    # Leer historial existente o iniciar una lista nueva
    if os.path.exists(HISTORIAL_PATH):
        with open(HISTORIAL_PATH, "r") as f:
            historial = json.load(f)
    else:
        historial = []

    nuevo_id = len(historial) + 1

    operacion = crear_operacion(
        nuevo_id, tipo, ticker, cantidad, monto_usdt, precio_unitario
    )
    historial.insert(0, operacion)

    # Guardar el historial actualizado
    with open(HISTORIAL_PATH, "w") as f:
        json.dump(historial, f, indent=4)


def trading():
    criptos = (
        cargar_datos_cotizaciones()
    )  # Esto devuelve una lista de diccionarios desde el json de cotizaciones
    estado = (
        obtener_estado()
    )  # Esto devuelve un diccionario del valor de USDT y demás criptos que estén en billetera

    print(estado)
    if request.method == "POST":
        exito, mensaje = procesar_operacion_trading(
            request.form
        )  # Es lo que trae Flask desde el formulario de trading.html. ALGO ASI: request.form = { "ticker": "BTC", "monto": "5000", "accion": "comprar"}
        flash(mensaje, "success" if exito else "danger")
        return redirect(url_for("trading"))

    return render_template("trading.html", criptos=criptos, estado=estado)
