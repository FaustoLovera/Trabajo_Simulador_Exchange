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