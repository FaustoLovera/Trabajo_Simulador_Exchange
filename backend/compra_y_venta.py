from flask import request, redirect, url_for, render_template, flash
import json
import os

COTIZACIONES_PATH = "./datos/datos_cotizaciones.json"
BILLETERA_PATH = "./datos/billetera.json"
HISTORIAL_PATH = "./datos/historial_operaciones.json"


def cargar_datos_cotizaciones():
    """
    Carga los datos de cotizaciones de criptomonedas desde un archivo JSON.

    Intenta abrir y leer el archivo especificado por `COTIZACIONES_PATH`. Si el archivo
    se encuentra, retorna su contenido como una lista de criptomonedas. Si el archivo
    no existe, retorna una lista vacía.
    """
    try:
        with open(COTIZACIONES_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró el archivo de cotizaciones locales.")
        return []


def obtener_precio(ticker):
    """
    Obtiene el precio actual de una criptomoneda específica.

    Lee el archivo de cotizaciones y busca el precio en USD de la criptomoneda
    cuyo ticker coincide con el proporcionado. Si el archivo no existe o 
    la criptomoneda no se encuentra, retorna None.
    """

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
    """
    Procesa una operación de trading en base a un formulario.

    El formulario debe contener los campos "ticker", "accion" y "monto".

    La función devuelve un par (booleano, mensaje), donde booleano indica
    si la operación se realizó con éxito y el mensaje es una descripción
    de lo sucedido.

    Si la acción es "comprar", la función llama a comprar_cripto y devuelve
    su resultado.

    Si la acción es "vender", la función llama a vender_cripto y devuelve
    su resultado.

    Si la acción no es ninguna de las anteriores, la función devuelve False
    y el mensaje "❌ Acción inválida."
    """
    
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
    """
    Carga la billetera desde un archivo JSON.

    Si el archivo especificado por `BILLETERA_PATH` no existe, se crea un archivo
    con un saldo inicial de 100,000 USDT y se retorna este saldo inicial. Si el archivo
    ya existe, se carga su contenido y se retorna como un diccionario.

    Asegura que el directorio del archivo exista antes de intentar crear o leer el archivo.
    """

    os.makedirs(os.path.dirname(BILLETERA_PATH), exist_ok=True)

    if not os.path.exists(BILLETERA_PATH):
        billetera_inicial = {"USDT": 100000}
        with open(BILLETERA_PATH, "w") as f:
            json.dump(billetera_inicial, f, indent=4)
        return billetera_inicial

    with open(BILLETERA_PATH, "r") as f:
        return json.load(f)


def guardar_billetera(billetera):
    """
    Guarda la billetera en un archivo JSON.

    Asegura que el directorio del archivo exista antes de intentar escribir el archivo.

    """
    with open(BILLETERA_PATH, "w") as f:
        json.dump(billetera, f, indent=4)


obtener_estado = lambda: cargar_billetera()


def comprar_cripto(ticker, monto_usd):
    """
    Ejecuta una operación de compra de una criptomoneda usando saldo en USDT disponible en la billetera.

    Verifica que el ticker exista y que haya saldo suficiente. Si la compra es posible, descuenta el monto
    en USDT, suma la cantidad adquirida de la criptomoneda a la billetera y actualiza el historial de operaciones.

    Devuelve un mensaje indicando si la compra fue exitosa o si ocurrió algún error.
    """
    
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
    """
    Ejecuta una operación de venta de una criptomoneda, acreditando el monto en USDT en la billetera.

    Verifica que el ticker exista, que haya suficiente cantidad disponible para vender y calcula el monto
    recibido en base al precio actual. Actualiza los saldos en la billetera, elimina la criptomoneda si el saldo
    queda en cero y registra la operación en el historial.

    Devuelve un mensaje indicando si la venta fue exitosa o si ocurrió algún error.
    """
    
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
    """
    Guarda una nueva operación en el historial de transacciones. La operación se guarda en formato JSON
    y se agrega al inicio del historial existente.

    Esta función realiza las siguientes tareas:
    1. Verifica si el archivo de historial existe. Si no existe, crea uno nuevo.
    2. Crea una operación con los parámetros proporcionados (tipo de operación, ticker, cantidad, monto en USDT, precio unitario).
    3. Asigna un identificador único a la operación, basado en el tamaño actual del historial.
    4. Inserta la nueva operación al principio del historial.
    5. Guarda el historial actualizado en el archivo JSON.

    La operación se guarda en un archivo JSON en la ruta definida por `HISTORIAL_PATH`.
    """
    
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
    """
    Maneja las operaciones de trading, procesando solicitudes de compra o venta de criptomonedas. 
    Carga las cotizaciones actuales de las criptomonedas y el estado de la billetera, mostrando 
    la información en un formulario de trading. Si se recibe una solicitud de tipo POST, procesa 
    la operación y muestra un mensaje de éxito o error, redirigiendo al usuario de vuelta a la página 
    de trading. Si la solicitud es GET, renderiza el formulario con las cotizaciones y el estado actual de la billetera.
    """
    
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
