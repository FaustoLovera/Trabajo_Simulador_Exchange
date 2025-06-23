"""
Servicio para la lógica de negocio de operaciones de trading (swap).

Este módulo contiene toda la lógica para procesar, validar y ejecutar un
intercambio de criptomonedas, incluyendo el cálculo y cobro de comisiones.
"""

from decimal import Decimal, InvalidOperation
from typing import Tuple

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_historial import guardar_en_historial
# Importamos el nuevo registrador de comisiones y la tasa desde la configuración.
from backend.acceso_datos.datos_comisiones import registrar_comision
from config import TASA_COMISION


def procesar_operacion_trading(formulario: dict) -> Tuple[bool, str]:
    """
    Valida y traduce los datos de un formulario de trading a una operación de swap.

    Esta función actúa como una capa de adaptación entre la vista y la lógica de
    negocio. Extrae, valida y convierte los datos del formulario antes de
    invocar a la función principal `realizar_swap`.
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

    return realizar_swap(moneda_origen, moneda_destino, monto_form, modo_ingreso, accion)


def _calcular_detalles_swap_bruto(
    accion: str,
    modo_ingreso: str,
    monto_form: Decimal,
    precio_origen_usdt: Decimal,
    precio_destino_usdt: Decimal
) -> dict:
    """
    Calcula las cantidades de origen y destino ANTES de aplicar comisiones.
    Esta función es ahora un cálculo puro sin validaciones lógicas de negocio.
    """
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
        # En modo venta, el único modo permitido es 'monto' (cantidad de cripto a vender).
        cantidad_origen = monto_form
        valor_total_usd = cantidad_origen * precio_origen_usdt
        cantidad_destino = valor_total_usd / precio_destino_usdt

    return {
        "origen": cantidad_origen,
        "destino": cantidad_destino,
        "valor_usd": valor_total_usd
    }


def _validar_saldo_suficiente(billetera: dict, moneda_origen: str, cantidad_requerida: Decimal) -> Tuple[bool, str | None]:
    """Verifica si hay suficiente saldo en la billetera para la operación."""
    saldo_disponible = billetera.get(moneda_origen, Decimal("0"))
    if cantidad_requerida > saldo_disponible:
        mensaje_error = f"❌ Saldo insuficiente. Tienes {saldo_disponible:.8f} {moneda_origen} pero se requieren {cantidad_requerida:.8f}."
        return False, mensaje_error
    return True, None


def _actualizar_billetera_y_guardar(billetera: dict, moneda_origen: str, cantidad_origen_total: Decimal, moneda_destino: str, cantidad_destino_neta: Decimal):
    """
    Actualiza los saldos en la billetera y persiste los cambios.
    Resta la cantidad TOTAL de origen y suma la NETA de destino.
    """
    billetera[moneda_origen] -= cantidad_origen_total
    
    if billetera[moneda_origen] <= Decimal("1e-8"):
        billetera.pop(moneda_origen, None)

    billetera[moneda_destino] = billetera.get(moneda_destino, Decimal("0")) + cantidad_destino_neta
    
    guardar_billetera(billetera)


def _registrar_operacion_historial(moneda_origen: str, cantidad_origen_neta: Decimal, moneda_destino: str, cantidad_destino_neta: Decimal, valor_usd_neto: Decimal):
    """Guarda la operación NETA (después de comisión) en el historial."""
    if moneda_origen == "USDT":
        tipo_operacion = "compra"
    elif moneda_destino == "USDT":
        tipo_operacion = "venta"
    else:
        tipo_operacion = "intercambio"
        
    guardar_en_historial(
        tipo_operacion,
        moneda_origen,
        cantidad_origen_neta.quantize(Decimal("0.00000001")),
        moneda_destino,
        cantidad_destino_neta.quantize(Decimal("0.00000001")),
        valor_usd_neto,
    )


def realizar_swap(moneda_origen: str, moneda_destino: str, monto_form: Decimal, modo_ingreso: str, accion: str) -> Tuple[bool, str]:
    """
    Orquesta la operación de swap completa, incluyendo el cálculo de comisiones.
    """
    # 1. Validaciones previas de la lógica de negocio
    if accion == 'vender' and modo_ingreso == 'total':
        return False, "❌ Al vender, debe ingresar la cantidad en modo 'Cantidad (Cripto)'."

    # 2. Obtener precios actuales
    precio_origen_usdt = obtener_precio(moneda_origen)
    precio_destino_usdt = obtener_precio(moneda_destino)

    if precio_origen_usdt is None or precio_destino_usdt is None or precio_origen_usdt.is_zero() or precio_destino_usdt.is_zero():
        return False, "❌ No se pudo obtener la cotización para realizar el swap."

    # 3. Calcular los detalles BRUTOS del swap (lo que el usuario quiere, antes de fees)
    resultado_bruto = _calcular_detalles_swap_bruto(
        accion, modo_ingreso, monto_form, precio_origen_usdt, precio_destino_usdt
    )
    cantidad_origen_bruta = resultado_bruto["origen"]

    # 4. Calcular y registrar la comisión
    # La comisión se cobra sobre la cantidad de la moneda que el usuario está entregando.
    cantidad_comision = cantidad_origen_bruta * TASA_COMISION
    valor_comision_usd = cantidad_comision * precio_origen_usdt
    
    # La cantidad total a debitar de la billetera es la cantidad bruta (swap + comisión)
    cantidad_total_a_debitar = cantidad_origen_bruta

    # 5. Cargar billetera y validar que el saldo sea suficiente para la operación + comisión
    billetera = cargar_billetera()
    exito_validacion, mensaje_error = _validar_saldo_suficiente(billetera, moneda_origen, cantidad_total_a_debitar)
    if not exito_validacion:
        return False, mensaje_error

    # --- A partir de aquí, la operación es válida y se ejecutará ---
    
    # 6. Registrar la comisión cobrada
    registrar_comision(moneda_origen, cantidad_comision, valor_comision_usd)

    # 7. Calcular las cantidades NETAS finales del intercambio
    cantidad_origen_neta_swap = cantidad_origen_bruta - cantidad_comision
    valor_neto_usd = cantidad_origen_neta_swap * precio_origen_usdt
    cantidad_destino_neta = valor_neto_usd / precio_destino_usdt

    # 8. Ejecutar la operación en la billetera
    _actualizar_billetera_y_guardar(
        billetera,
        moneda_origen,
        cantidad_total_a_debitar,
        moneda_destino,
        cantidad_destino_neta
    )
    
    # 9. Registrar la operación NETA en el historial
    _registrar_operacion_historial(
        moneda_origen,
        cantidad_origen_neta_swap,
        moneda_destino,
        cantidad_destino_neta,
        valor_neto_usd
    )

    # 10. Devolver mensaje de éxito detallado
    mensaje_exito = (
        f"✅ Operación exitosa: Se intercambiaron {cantidad_origen_neta_swap:.8f} {moneda_origen} "
        f"por {cantidad_destino_neta:.8f} {moneda_destino}. "
        f"Comisión aplicada: {cantidad_comision:.8f} {moneda_origen}."
    )
    return True, mensaje_exito