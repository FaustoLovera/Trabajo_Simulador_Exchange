from decimal import Decimal, InvalidOperation
from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_historial import guardar_en_historial


def procesar_operacion_trading(formulario):
    """
    TRADUCTOR: Recibe el formulario y lo convierte en una llamada a `realizar_swap`.
    """
    try:
        ticker_principal = formulario["ticker"].upper()
        accion = formulario["accion"]
        monto_form = Decimal(formulario["monto"])
        modo_ingreso = formulario["modo-ingreso"]
    except (KeyError, InvalidOperation, TypeError):
        return False, "❌ Error en los datos del formulario."

    if monto_form <= 0:
        return False, "❌ El monto debe ser un número positivo."

    # Lógica de traducción mucho más clara
    if accion == "comprar":
        moneda_origen = formulario.get("moneda-pago", "USDT").upper()
        moneda_destino = ticker_principal
    elif accion == "vender":
        moneda_origen = ticker_principal
        moneda_destino = formulario.get("moneda-recibir", "USDT").upper()
    else:
        return False, "❌ Acción no válida."

    if moneda_origen == moneda_destino:
        return False, "❌ La moneda de origen y destino no pueden ser la misma."

    # Pasamos la acción para que la función de swap también la conozca
    return realizar_swap(moneda_origen, moneda_destino, monto_form, modo_ingreso, accion)


def realizar_swap(moneda_origen, moneda_destino, monto_form, modo_ingreso, accion):
    """
    EJECUTOR: Orquesta la operación de swap completa.
    """
    precio_origen_usdt = obtener_precio(moneda_origen)
    precio_destino_usdt = obtener_precio(moneda_destino)

    if precio_origen_usdt is None or precio_destino_usdt is None or precio_destino_usdt.is_zero():
        return False, "❌ No se pudo obtener la cotización para realizar el swap."

    # --- LÓGICA DE CÁLCULO CORREGIDA Y SIMPLIFICADA ---
    if accion == "comprar":
        if modo_ingreso == "monto":  # Usuario ingresó la cantidad de CRIPTO a recibir (destino)
            cantidad_destino = monto_form
            valor_total_usd = cantidad_destino * precio_destino_usdt
            cantidad_origen = valor_total_usd / precio_origen_usdt
        else:  # modo_ingreso == "total" - Usuario ingresó el total a GASTAR (origen)
            cantidad_origen = monto_form
            valor_total_usd = cantidad_origen * precio_origen_usdt
            cantidad_destino = valor_total_usd / precio_destino_usdt
    elif accion == "vender":
        if modo_ingreso == "total":
            return False, "❌ Al vender, debe ingresar la cantidad en modo 'Monto'."
        # Al vender, el monto del formulario SIEMPRE es la cantidad del activo origen.
        cantidad_origen = monto_form
        valor_total_usd = cantidad_origen * precio_origen_usdt
        cantidad_destino = valor_total_usd / precio_destino_usdt
    else:
        return False, "❌ Acción desconocida durante el cálculo."
        
    # --- FIN DE LA LÓGICA DE CÁLCULO ---

    billetera = cargar_billetera()
    saldo_disponible = billetera.get(moneda_origen, Decimal("0"))
    if cantidad_origen > saldo_disponible:
        return False, f"❌ Saldo insuficiente. Tienes {saldo_disponible:.8f} {moneda_origen}."

    billetera[moneda_origen] -= cantidad_origen
    if billetera[moneda_origen] <= Decimal("1e-8"):
        billetera.pop(moneda_origen, None)
    
    billetera[moneda_destino] = billetera.get(moneda_destino, Decimal("0")) + cantidad_destino
    guardar_billetera(billetera)

    tipo_operacion = "compra" if moneda_origen == "USDT" else "venta" if moneda_destino == "USDT" else "intercambio"
    guardar_en_historial(
        tipo_operacion,
        moneda_origen,
        cantidad_origen.quantize(Decimal("0.00000001")),
        moneda_destino,
        cantidad_destino.quantize(Decimal("0.00000001")),
        valor_total_usd,
    )

    mensaje = f"✅ Swap: {cantidad_origen:.8f} {moneda_origen} → {cantidad_destino:.8f} {moneda_destino}."
    return True, mensaje