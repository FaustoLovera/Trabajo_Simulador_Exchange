from decimal import Decimal, InvalidOperation
from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_historial import guardar_en_historial

def procesar_operacion_trading(formulario):
    """
    Procesa una operación del formulario "Comprar/Vender" y la traduce
    a una operación de SWAP universal, manejando todos los modos de ingreso.
    """
    try:
        ticker_principal = formulario["ticker"].upper()
        accion = formulario["accion"]
        monto_form = Decimal(formulario["monto"])
        modo_ingreso = formulario["modo-ingreso"]
    except (KeyError, InvalidOperation):
        return False, "❌ Error en los datos del formulario."

    if monto_form <= 0:
        return False, "❌ El monto debe ser mayor a 0."

    moneda_origen, moneda_destino, cantidad_origen = (None, None, None)
    
    # --- TRADUCCIÓN DE LA LÓGICA DE FORMULARIO A SWAP ---
    if accion == "comprar":
        moneda_destino = ticker_principal
        moneda_origen = formulario.get("moneda-pago", "USDT").upper()

        precio_destino = obtener_precio(moneda_destino)
        precio_origen = obtener_precio(moneda_origen)
        if precio_destino is None or precio_origen is None or precio_origen.is_zero():
            return False, "❌ No se encontraron las cotizaciones para la operación."

        if modo_ingreso == "monto": 
            costo_total_usd = monto_form * precio_destino
            cantidad_origen = costo_total_usd / precio_origen
        else: # "total"
            costo_total_usd = monto_form
            cantidad_origen = costo_total_usd / precio_origen

    elif accion == "vender":
        moneda_origen = ticker_principal
        moneda_destino = formulario.get("moneda-recibir", "USDT").upper()
        
        # --- LÓGICA CORREGIDA PARA VENTA POR VALOR ---
        if modo_ingreso == "monto":
            # Si el modo es "monto", la cantidad de origen es directamente el monto del formulario.
            cantidad_origen = monto_form
        else: # modo_ingreso == "total"
            # Si el modo es "total", el monto del formulario es el valor en USD que se desea obtener.
            # Necesitamos calcular cuánta moneda_origen se necesita vender.
            precio_origen = obtener_precio(moneda_origen)
            if precio_origen is None or precio_origen.is_zero():
                return False, f"❌ No se pudo obtener el precio de {moneda_origen} para calcular la venta."
            
            # Calculamos la cantidad de la cripto a vender para alcanzar el total deseado.
            cantidad_origen = monto_form / precio_origen

    # --- Validaciones finales y ejecución ---
    if moneda_origen == moneda_destino:
        return False, "❌ La moneda de origen y destino no pueden ser la misma."

    if moneda_origen and moneda_destino and cantidad_origen is not None:
        return realizar_swap(moneda_origen, moneda_destino, cantidad_origen)
    else:
        return False, "❌ Error al procesar la operación."


def realizar_swap(moneda_origen, moneda_destino, cantidad_origen):
    """
    Función universal de SWAP. No necesita más cambios.
    """
    billetera = cargar_billetera()
    cantidad_origen = cantidad_origen.quantize(Decimal("0.00000001"))

    # Verificar saldo
    saldo_disponible = billetera.get(moneda_origen, Decimal("0"))
    if cantidad_origen > saldo_disponible:
        return False, f"❌ Saldo insuficiente. Tienes {saldo_disponible:.8f} {moneda_origen} pero se necesitan {cantidad_origen:.8f}."

    # Obtener precios
    precio_origen = obtener_precio(moneda_origen)
    precio_destino = obtener_precio(moneda_destino)
    if precio_origen is None or precio_destino is None or precio_destino.is_zero():
        return False, "❌ No se pudo obtener la cotización para realizar el swap."

    # Calcular equivalencia y actualizar billetera
    valor_en_usd = cantidad_origen * precio_origen
    cantidad_destino = (valor_en_usd / precio_destino).quantize(Decimal("0.00000001"))

    billetera[moneda_origen] -= cantidad_origen
    if billetera[moneda_origen].is_zero():
        billetera.pop(moneda_origen)

    billetera[moneda_destino] = billetera.get(moneda_destino, Decimal("0")) + cantidad_destino

    guardar_billetera(billetera)
    
    mensaje = (
        f"✅ Swap exitoso: Intercambiaste {cantidad_origen:.8f} {moneda_origen} "
        f"por {cantidad_destino:.8f} {moneda_destino}."
    )
    return True, mensaje