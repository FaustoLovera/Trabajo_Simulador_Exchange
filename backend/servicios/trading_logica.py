from decimal import Decimal, InvalidOperation
from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_historial import guardar_en_historial

# --- FUNCIÓN DE PROCESAMIENTO DEL FORMULARIO ---

def procesar_operacion_trading(formulario):
    """
    TRADUCTOR: Recibe el formulario, lo valida y lo convierte en una llamada
    a la lógica de negocio principal (`realizar_swap`).
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

    # Determina las monedas de la operación basándose en la acción
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

    # Llama a la lógica principal con los datos ya limpios y preparados
    return realizar_swap(moneda_origen, moneda_destino, monto_form, modo_ingreso, accion)


# --- FUNCIONES AUXILIARES INTERNAS (LÓGICA DE NEGOCIO) ---

def _calcular_detalles_swap(accion, modo_ingreso, monto_form, precio_origen_usdt, precio_destino_usdt):
    """
    Calcula las cantidades de origen, destino y el valor total en USD del swap.
    Esta es una función interna y pura que solo realiza cálculos.

    Returns:
        tuple: (True, {'origen': cant, 'destino': cant, 'valor_usd': val}) o (False, "error").
    """
    # Validación de entrada específica para esta lógica
    if accion == 'vender' and modo_ingreso == 'total':
        return False, "❌ Al vender, debe ingresar la cantidad en modo 'Monto' (Cripto)."

    if accion not in ['comprar', 'vender']:
        return False, "❌ Acción de trading desconocida."

    # Lógica de cálculo
    if accion == 'comprar':
        if modo_ingreso == 'monto':  # Usuario ingresa la cantidad de CRIPTO a recibir
            cantidad_destino = monto_form
            valor_total_usd = cantidad_destino * precio_destino_usdt
            cantidad_origen = valor_total_usd / precio_origen_usdt
        else:  # 'total', usuario ingresa la cantidad de FIAT a gastar
            cantidad_origen = monto_form
            valor_total_usd = cantidad_origen * precio_origen_usdt
            cantidad_destino = valor_total_usd / precio_destino_usdt
    else:  # accion == 'vender'
        cantidad_origen = monto_form
        valor_total_usd = cantidad_origen * precio_origen_usdt
        cantidad_destino = valor_total_usd / precio_destino_usdt

    detalles = {
        "origen": cantidad_origen,
        "destino": cantidad_destino,
        "valor_usd": valor_total_usd
    }
    return True, detalles


def _validar_saldo_suficiente(billetera, moneda_origen, cantidad_requerida):
    """Verifica si hay suficiente saldo en la billetera para la operación."""
    saldo_disponible = billetera.get(moneda_origen, Decimal("0"))
    if cantidad_requerida > saldo_disponible:
        mensaje_error = f"❌ Saldo insuficiente. Tienes {saldo_disponible:.8f} {moneda_origen}."
        return False, mensaje_error
    return True, None


def _actualizar_billetera_y_guardar(billetera, moneda_origen, cantidad_origen, moneda_destino, cantidad_destino):
    """Resta la moneda de origen, suma la de destino y guarda el estado final."""
    billetera[moneda_origen] -= cantidad_origen
    
    # Si el saldo es muy pequeño ("polvo"), se elimina la moneda de la billetera
    if billetera[moneda_origen] <= Decimal("1e-8"):
        billetera.pop(moneda_origen, None)

    billetera[moneda_destino] = billetera.get(moneda_destino, Decimal("0")) + cantidad_destino
    
    guardar_billetera(billetera)


def _registrar_operacion_historial(moneda_origen, cantidad_origen, moneda_destino, cantidad_destino, valor_usd):
    """Determina el tipo de operación y la guarda en el historial."""
    if moneda_origen == "USDT":
        tipo_operacion = "compra"
    elif moneda_destino == "USDT":
        tipo_operacion = "venta"
    else:
        tipo_operacion = "intercambio"
        
    guardar_en_historial(
        tipo_operacion,
        moneda_origen,
        cantidad_origen.quantize(Decimal("0.00000001")),
        moneda_destino,
        cantidad_destino.quantize(Decimal("0.00000001")),
        valor_usd,
    )


# --- FUNCIÓN ORQUESTADORA PRINCIPAL ---

def realizar_swap(moneda_origen, moneda_destino, monto_form, modo_ingreso, accion):
    """
    Orquesta la operación de swap completa: obtiene precios, calcula, valida y ejecuta.
    """
    # 1. Obtener precios
    precio_origen_usdt = obtener_precio(moneda_origen)
    precio_destino_usdt = obtener_precio(moneda_destino)

    if precio_origen_usdt is None or precio_destino_usdt is None or precio_destino_usdt.is_zero():
        return False, "❌ No se pudo obtener la cotización para realizar el swap."

    # 2. Calcular los detalles del swap
    exito_calculo, resultado = _calcular_detalles_swap(
        accion, modo_ingreso, monto_form, precio_origen_usdt, precio_destino_usdt
    )
    if not exito_calculo:
        return False, resultado  # resultado aquí es el mensaje de error

    cantidad_origen = resultado["origen"]
    cantidad_destino = resultado["destino"]
    valor_total_usd = resultado["valor_usd"]

    # 3. Cargar billetera y validar saldo
    billetera = cargar_billetera()
    exito_validacion, mensaje_error = _validar_saldo_suficiente(billetera, moneda_origen, cantidad_origen)
    if not exito_validacion:
        return False, mensaje_error

    # 4. Ejecutar la operación (si todo es válido hasta ahora)
    _actualizar_billetera_y_guardar(billetera, moneda_origen, cantidad_origen, moneda_destino, cantidad_destino)
    
    # 5. Registrar en el historial
    _registrar_operacion_historial(moneda_origen, cantidad_origen, moneda_destino, cantidad_destino, valor_total_usd)

    # 6. Devolver mensaje de éxito
    mensaje_exito = f"✅ Swap exitoso: {cantidad_origen:.8f} {moneda_origen} → {cantidad_destino:.8f} {moneda_destino}."
    return True, mensaje_exito