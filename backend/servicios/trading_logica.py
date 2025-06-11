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

    if precio_destino_usdt == Decimal("0"):
        return None

    return (precio_origen_usdt / precio_destino_usdt).quantize(Decimal("0.00000001"))


def operar_par(origen, destino, cantidad_origen, cantidad_destino, precio_relativo, tipo_operacion="intercambio"):
    """
    Ejecuta la operación de intercambio entre dos criptomonedas y actualiza la billetera.
    Registra la operación en el historial.
    """
    billetera = cargar_billetera()
    saldo_origen = billetera.get(origen, Decimal("0"))

    if cantidad_origen > saldo_origen:
        return False, f"❌ Saldo insuficiente en {origen}. Disponible: {saldo_origen:.6f}"

    billetera[origen] -= cantidad_origen
    billetera[destino] = billetera.get(destino, Decimal("0")) + cantidad_destino

    if billetera[origen] <= Decimal("0"):
        billetera.pop(origen)

    guardar_billetera(billetera)
    guardar_en_historial(tipo_operacion, f"{origen} -> {destino}", cantidad_destino, cantidad_origen, precio_relativo)

    return True, f"✅ Intercambio exitoso: {cantidad_origen:.6f} {origen} → {cantidad_destino:.6f} {destino}"


def procesar_operacion_trading(formulario):
    """
    Procesa todas las operaciones de trading (compra, venta, intercambio) basándose en los datos del formulario.
    El 'modo_ingreso' debe ser siempre 'cantidad_origen' o 'cantidad_destino'.
    """
    origen_cripto = formulario.get("origen", "").upper()
    destino_cripto = formulario.get("destino", "").upper()
    # Ahora, 'modo_ingreso' siempre indicará si el 'monto' es de la cripto de origen o destino
    modo_ingreso = formulario.get("modo-ingreso", "")
    tipo_orden = formulario.get("tipo-orden", "")

    try:
        monto = Decimal(formulario["monto"])
    except (KeyError, InvalidOperation):
        return False, "❌ Monto inválido."

    # Validaciones básicas
    if not origen_cripto or not destino_cripto:
        return False, "❌ Faltan cripto origen o destino."

    if origen_cripto == destino_cripto:
        return False, "❌ Las criptos origen y destino deben ser distintas."

    if monto <= 0:
        return False, "❌ El monto debe ser mayor a 0."

    if tipo_orden not in ["mercado", "limite", "stop-limit"]:
        return False, "❌ Tipo de orden inválido."

    # Validar los nuevos modos de ingreso
    if modo_ingreso not in ["cantidad_origen", "cantidad_destino"]:
        return False, "❌ Modo de ingreso inválido. Debe ser 'cantidad_origen' o 'cantidad_destino'."

    precio_relativo_destino_por_origen = obtener_precio_relativo(origen_cripto, destino_cripto)
    if precio_relativo_destino_por_origen is None:
        return False, f"❌ No se puede obtener el precio entre {origen_cripto} y {destino_cripto}."

    # Determinar el tipo de operación para el registro en el historial.
    if origen_cripto == "USDT":
        tipo_operacion_historial = "compra"
    elif destino_cripto == "USDT":
        tipo_operacion_historial = "venta"
    else:
        tipo_operacion_historial = "intercambio"

    cantidad_origen = Decimal("0")
    cantidad_destino = Decimal("0")

    # Lógica de cálculo unificada y simplificada:
    # Si el monto ingresado es la cantidad de origen, calcula destino.
    if modo_ingreso == "cantidad_origen":
        cantidad_origen = monto
        cantidad_destino = (cantidad_origen * precio_relativo_destino_por_origen).quantize(Decimal("0.00000001"))
    # Si el monto ingresado es la cantidad de destino, calcula origen.
    elif modo_ingreso == "cantidad_destino":
        cantidad_destino = monto
        cantidad_origen = (cantidad_destino / precio_relativo_destino_por_origen).quantize(Decimal("0.00000001"))
    
    # Nota: No hay un caso para 'valor_usdt' aquí directamente. Esa conversión la manejan los wrappers.

    resultado = operar_par(origen_cripto, destino_cripto, cantidad_origen, cantidad_destino, precio_relativo_destino_por_origen, tipo_operacion_historial)

    if resultado is None:
        return False, "❌ Error inesperado al procesar la operación."

    return resultado


def comprar_cripto(ticker_a_comprar, monto_usdt_a_gastar_o_cantidad_a_recibir, modo_compra="gastar_usdt"):
    """
    Función para comprar una criptomoneda usando USDT.
    Flexible para especificar cuánto USDT gastar o cuánta cripto recibir.

    Args:
        ticker_a_comprar (str): El ticker de la criptomoneda que se desea comprar (destino).
        monto_usdt_a_gastar_o_cantidad_a_recibir (Decimal): La cantidad de USDT a gastar O la cantidad de cripto a recibir.
        modo_compra (str): "gastar_usdt" si el monto es el USDT a gastar.
                           "recibir_cripto" si el monto es la cantidad de cripto a recibir.
    """
    formulario = {
        "origen": "USDT",
        "destino": ticker_a_comprar.upper(),
        "tipo-orden": "mercado",
        "monto": str(monto_usdt_a_gastar_o_cantidad_a_recibir)
    }

    if modo_compra == "gastar_usdt":
        formulario["modo-ingreso"] = "cantidad_origen" # Gastar esta cantidad de USDT (origen)
    elif modo_compra == "recibir_cripto":
        formulario["modo-ingreso"] = "cantidad_destino" # Recibir esta cantidad de la cripto (destino)
    else:
        return False, "❌ Modo de compra inválido. Debe ser 'gastar_usdt' o 'recibir_cripto'."
    
    return procesar_operacion_trading(formulario)


def vender_cripto(ticker_a_vender, cantidad_o_valor_a_vender, destino_cripto="USDT", modo_venta="cantidad_cripto"):
    """
    Función para vender una criptomoneda y obtener USDT o cualquier otra cripto.

    Args:
        ticker_a_vender (str): El ticker de la criptomoneda que se desea vender (origen).
        cantidad_o_valor_a_vender (Decimal):
            - Si modo_venta="cantidad_cripto", es la cantidad de la cripto de origen a vender (ej. 1 ETH).
            - Si modo_venta="valor_usdt", es el valor en USDT de la cripto de origen a vender (ej. 200 USDT de ETH).
            - Si modo_venta="recibir_destino", es la cantidad de la cripto destino que se desea recibir (ej. 100 USDT).
        destino_cripto (str): El ticker de la criptomoneda que se desea recibir (destino). Por defecto es "USDT".
        modo_venta (str): Define qué representa 'cantidad_o_valor_a_vender'. Puede ser "cantidad_cripto", "valor_usdt" o "recibir_destino".
                          Por defecto es "cantidad_cripto".
    """
    formulario = {
        "origen": ticker_a_vender.upper(),
        "destino": destino_cripto.upper(),
        "tipo-orden": "mercado",
        "monto": str(cantidad_o_valor_a_vender)
    }

    if modo_venta == "cantidad_cripto":
        # Usuario dice: "quiero vender X cantidad de mi cripto de origen" (ej. 1 ETH)
        formulario["modo-ingreso"] = "cantidad_origen"
    elif modo_venta == "recibir_destino":
        # Usuario dice: "quiero recibir X cantidad de mi cripto de destino" (ej. 100 USDT)
        formulario["modo-ingreso"] = "cantidad_destino"
    elif modo_venta == "valor_usdt":
        # Usuario dice: "quiero vender X valor USDT de mi cripto de origen" (ej. 200 USDT de ETH)
        # Aquí necesitamos un paso intermedio para convertir el valor USDT a cantidad de origen.
        precio_origen_usdt = obtener_precio(ticker_a_vender)
        if precio_origen_usdt is None or precio_origen_usdt == Decimal("0"):
            return False, f"❌ No se puede obtener el precio de {ticker_a_vender} en USDT para calcular el valor."
        
        # Calcular la cantidad de la cripto de origen que representa ese valor en USDT
        cantidad_origen_calculada = (cantidad_o_valor_a_vender / precio_origen_usdt).quantize(Decimal("0.00000001"))
        
        formulario["modo-ingreso"] = "cantidad_origen"
        formulario["monto"] = str(cantidad_origen_calculada) # Reemplazar el monto con la cantidad calculada
    else:
        return False, "❌ Modo de venta inválido. Debe ser 'cantidad_cripto', 'recibir_destino' o 'valor_usdt'."
    
    return procesar_operacion_trading(formulario)