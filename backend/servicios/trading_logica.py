from decimal import Decimal
from acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from acceso_datos.datos_cotizaciones import obtener_precio
from acceso_datos.datos_historial import guardar_en_historial


def procesar_operacion_trading(formulario):
    ticker = formulario["ticker"]
    accion = formulario["accion"]
    monto = Decimal(formulario["monto"])

    if accion == "comprar":
        return comprar_cripto(ticker, monto)
    elif accion == "vender":
        return vender_cripto(ticker, monto)
    else:
        return False, "❌ Acción inválida."


def comprar_cripto(ticker, monto_usd):
    billetera = cargar_billetera()
    precio = obtener_precio(ticker)

    if precio is None:
        return False, f"❌ No se encontró el ticker {ticker}"

    if monto_usd > billetera["USDT"]:
        return False, "❌ Saldo insuficiente"

    billetera["USDT"] -= monto_usd

    cantidad = (monto_usd / precio).quantize(Decimal("0.00000001"))
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

    cantidad_actual = billetera.get(ticker, Decimal("0"))

    if cantidad_actual < cantidad_a_vender:
        return (
            False,
            f"❌ No tenés suficiente {ticker} para vender (disponible: {cantidad_actual:.6f})",
        )

    monto_usd = cantidad_a_vender * precio
    billetera["USDT"] += monto_usd
    billetera[ticker] = cantidad_actual - cantidad_a_vender

    if billetera[ticker] <= Decimal('0'):
        billetera.pop(ticker)

    guardar_billetera(billetera)
    guardar_en_historial("venta", ticker, cantidad_a_vender, monto_usd, precio)
    return (
        True,
        f"✅ Venta exitosa: {cantidad_a_vender:.6f} {ticker} por ${monto_usd:.2f}",
    )
