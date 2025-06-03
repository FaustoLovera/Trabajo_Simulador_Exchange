from decimal import Decimal, InvalidOperation
from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_historial import guardar_en_historial

def obtener_precio_relativo(origen, destino):
    """
    Retorna cuántas unidades de destino se obtienen por 1 unidad de origen.
    Ej: si origen=BTC y destino=ETH, y 1 BTC = 15 ETH, retorna 15.
    """
    precio_origen_usdt = obtener_precio(origen)
    precio_destino_usdt = obtener_precio(destino)

    if precio_origen_usdt is None or precio_destino_usdt is None:
        return None

    return (precio_origen_usdt / precio_destino_usdt).quantize(Decimal("0.00000001"))


def operar_par(origen, destino, cantidad_origen, cantidad_destino, precio_relativo):
    billetera = cargar_billetera()
    saldo_origen = billetera.get(origen, Decimal("0"))

    if cantidad_origen > saldo_origen:
        return False, f"❌ Saldo insuficiente en {origen}. Disponible: {saldo_origen:.6f}"

    # Ejecutar operación
    billetera[origen] -= cantidad_origen
    billetera[destino] = billetera.get(destino, Decimal("0")) + cantidad_destino

    if billetera[origen] <= Decimal("0"):
        billetera.pop(origen)

    guardar_billetera(billetera)
    guardar_en_historial("compra", f"{origen} -> {destino}", cantidad_destino, cantidad_origen, precio_relativo)

    return True, f"✅ Intercambio exitoso: {cantidad_origen:.6f} {origen} → {cantidad_destino:.6f} {destino}"


def procesar_operacion_trading(formulario):
    origen_cripto = formulario.get("origen", "").upper()
    destino_cripto = formulario.get("destino", "").upper()
    modo_ingreso = formulario.get("modo-ingreso", "")  # "monto" o "total"
    tipo_orden = formulario.get("tipo-orden", "")  # "mercado", "limite", etc.

    try:
        monto = Decimal(formulario["monto"])
    except (KeyError, InvalidOperation):
        return False, "❌ Monto inválido."

    if not origen_cripto or not destino_cripto:
        return False, "❌ Faltan cripto origen o destino."

    if origen_cripto == destino_cripto:
        return False, "❌ Las criptos origen y destino deben ser distintas."

    if monto <= 0:
        return False, "❌ El monto debe ser mayor a 0."

    if tipo_orden not in ["mercado", "limite", "stop-limit"]:
        return False, "❌ Tipo de orden inválido."

    if modo_ingreso not in ["monto", "total"]:
        return False, "❌ Modo de ingreso inválido."

    # Obtener precio de conversión (ej: 1 BTC = ? ETH)
    precio = obtener_precio_relativo(origen_cripto, destino_cripto)
    if precio is None:
        return False, f"❌ No se puede obtener el precio entre {origen_cripto} y {destino_cripto}."

    if modo_ingreso == "monto":
        # Monto deseado en destino → calcular cuánto origen necesito gastar
        cantidad_destino = monto
        cantidad_origen = (cantidad_destino / precio).quantize(Decimal("0.00000001"))
    else:  # "total"
        # Total en origen a gastar → calcular cuánto destino recibo
        cantidad_origen = monto
        cantidad_destino = (cantidad_origen * precio).quantize(Decimal("0.00000001"))

        resultado = operar_par(origen_cripto, destino_cripto, cantidad_origen, cantidad_destino, precio)

        # Asegurarse de que siempre se devuelva una tupla
        if resultado is None:
            return False, "❌ Error inesperado al procesar la operación."

        return resultado

def comprar_cripto(ticker, monto_usd):
    billetera = cargar_billetera()
    precio = obtener_precio(ticker)

    if precio is None:
        return False, f"❌ No se encontró el ticker {ticker}."

    if monto_usd > billetera.get("USDT", Decimal("0")):
        return False, "❌ Saldo insuficiente en USDT."

    cantidad = (monto_usd / precio).quantize(Decimal("0.00000001"))

    billetera["USDT"] -= monto_usd
    billetera[ticker] = billetera.get(ticker, Decimal("0")) + cantidad

    guardar_billetera(billetera)
    guardar_en_historial("compra", ticker, cantidad, monto_usd, precio)
    return True, f"✅ Compra exitosa: {cantidad:.6f} {ticker} por ${monto_usd:.2f} USDT."


def vender_cripto(ticker, cantidad_a_vender):
    billetera = cargar_billetera()
    precio = obtener_precio(ticker)

    if precio is None:
        return False, f"❌ No se encontró el ticker {ticker}."

    cantidad_actual = billetera.get(ticker, Decimal("0"))

    if cantidad_a_vender > cantidad_actual:
        return (
            False,
            f"❌ No tenés suficiente {ticker} para vender (disponible: {cantidad_actual:.6f}).",
        )

    monto_usd = (cantidad_a_vender * precio).quantize(Decimal("0.01"))
    billetera[ticker] -= cantidad_a_vender
    billetera["USDT"] = billetera.get("USDT", Decimal("0")) + monto_usd

    if billetera[ticker] <= Decimal("0"):
        billetera.pop(ticker)

    guardar_billetera(billetera)
    guardar_en_historial("venta", ticker, cantidad_a_vender, monto_usd, precio)
    return True, f"✅ Venta exitosa: {cantidad_a_vender:.6f} {ticker} por ${monto_usd:.2f} USDT."
