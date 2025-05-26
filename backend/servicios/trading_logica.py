from decimal import Decimal, InvalidOperation
from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_historial import guardar_en_historial


def procesar_operacion_trading(formulario):
    try:
        ticker = formulario["ticker"].upper()
        accion = formulario["accion"]  # debe ser "comprar" o "vender"
        monto = Decimal(formulario["monto"])
        tipo_orden = formulario["tipo-orden"]
        modo_ingreso = formulario["modo-ingreso"]
    except (KeyError, InvalidOperation):
        return False, "❌ Error en los datos del formulario."

    if monto <= 0:
        return False, "❌ El monto debe ser mayor a 0."

    if tipo_orden not in ["mercado", "limite", "stop-limit"]:
        return False, "❌ Tipo de orden inválido."

    if modo_ingreso not in ["monto", "total"]:
        return False, "❌ Modo de ingreso inválido."

    if accion == "comprar":
        precio = obtener_precio(ticker)
        if precio is None:
            return False, f"❌ No se encontró el ticker {ticker}."
    
        if modo_ingreso == "monto":
            # El usuario quiere comprar X cantidad de cripto (monto = cantidad de cripto)
            monto_usd = (monto * precio).quantize(Decimal("0.01"))
            return comprar_cripto(ticker, monto_usd)
        else:  # total
            # El usuario quiere gastar X cantidad de USD (monto = monto_usd directamente)
            return comprar_cripto(ticker, monto)


    elif accion == "vender":
        # modo_ingreso:
        # "monto" -> monto es cantidad de cripto a vender
        # "total" -> monto es USD que se desea obtener (calcular cantidad cripto)
        if modo_ingreso == "monto":
            return vender_cripto(ticker, monto)
        else:  # total
            precio = obtener_precio(ticker)
            if precio is None:
                return False, f"❌ No se encontró el ticker {ticker}."
            cantidad = (monto / precio).quantize(Decimal("0.00000001"))
            return vender_cripto(ticker, cantidad)
    else:
        return False, "❌ Acción inválida."


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
