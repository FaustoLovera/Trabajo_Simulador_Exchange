# backend/servicios/trading/procesador.py

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Tuple, Dict, Any

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from config import ACCION_COMPRAR, ACCION_VENDER
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_ordenes import agregar_orden_pendiente
from backend.servicios.trading.ejecutar_orden import ejecutar_transaccion
from backend.utils.responses import crear_respuesta_error, crear_respuesta_exitosa
from backend.utils.utilidades_numericas import (
    a_decimal, cuantizar_cripto, cuantizar_usd, 
    formato_cantidad_cripto, formato_cantidad_usd
)

def _validar_saldo_disponible(billetera: dict, moneda_origen: str, cantidad_requerida: Decimal) -> Tuple[bool, str | None]:
    """Valida si hay suficiente saldo disponible en la billetera."""
    activo = billetera.get(moneda_origen)
    if not activo:
        return False, f"❌ No posees {moneda_origen} en tu billetera."
    saldo_disponible = a_decimal(activo['saldos'].get("disponible"))
    if cantidad_requerida > saldo_disponible:
        return False, f"❌ Saldo insuficiente. Tienes {formato_cantidad_cripto(saldo_disponible)} {moneda_origen} disponibles, pero se requieren {formato_cantidad_cripto(cantidad_requerida)}."
    return True, None

def _calcular_detalles_intercambio(
    accion: str,
    modo_ingreso: str,
    monto_form: Decimal,
    precio_origen_usdt: Decimal,
    precio_destino_usdt: Decimal
) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Función de cálculo pura para un intercambio.
    No modifica estado, solo realiza matemáticas. Devuelve las cantidades brutas.
    """
    if precio_origen_usdt.is_zero() or precio_destino_usdt.is_zero():
        return False, "No se pudo obtener una cotización válida para el par."

    cantidad_origen_bruta = Decimal("0")
    cantidad_destino_bruta = Decimal("0")
    valor_usd = Decimal("0")
    
    if accion == ACCION_COMPRAR:
        if modo_ingreso == "monto":
            cantidad_destino_bruta = monto_form
            valor_usd = cantidad_destino_bruta * precio_destino_usdt
            cantidad_origen_bruta = valor_usd / precio_origen_usdt
        elif modo_ingreso == "total":
            cantidad_origen_bruta = monto_form
            valor_usd = cantidad_origen_bruta * precio_origen_usdt
            cantidad_destino_bruta = valor_usd / precio_destino_usdt
        else:
            return False, f"Modo de ingreso '{modo_ingreso}' no válido para una compra."
    
    elif accion == "vender":
        if modo_ingreso == "monto":
            cantidad_origen_bruta = monto_form
            valor_usd = cantidad_origen_bruta * precio_origen_usdt
            cantidad_destino_bruta = valor_usd / precio_destino_usdt
        elif modo_ingreso == "total":
            cantidad_destino_bruta = monto_form
            valor_usd = cantidad_destino_bruta * precio_destino_usdt
            cantidad_origen_bruta = valor_usd / precio_origen_usdt
        else:
            return False, f"Modo de ingreso '{modo_ingreso}' no válido para una venta."
    
    else:
        return False, f"Acción de trading desconocida: '{accion}'."

    return True, {
        "cantidad_origen_bruta": cantidad_origen_bruta,
        "cantidad_destino_bruta": cantidad_destino_bruta,
        "valor_usd": valor_usd
    }
    
def _ejecutar_orden_mercado(moneda_origen: str, moneda_destino: str, monto_form: Decimal, modo_ingreso: str, accion: str) -> Dict[str, Any]:
    """Orquesta la ejecución de una orden a precio de mercado."""
    precio_origen_usdt = obtener_precio(moneda_origen)
    precio_destino_usdt = obtener_precio(moneda_destino)
    if not all([precio_origen_usdt, precio_destino_usdt]):
        return crear_respuesta_error("❌ No se pudo obtener la cotización para realizar el swap.")

    exito_calculo, detalles_brutos = _calcular_detalles_intercambio(accion, modo_ingreso, monto_form, precio_origen_usdt, precio_destino_usdt)
    if not exito_calculo:
        return crear_respuesta_error(f"❌ {detalles_brutos}")

    cantidad_origen_bruta = detalles_brutos["cantidad_origen_bruta"]
    billetera = cargar_billetera()
    exito_validacion, mensaje_error = _validar_saldo_disponible(billetera, moneda_origen, cantidad_origen_bruta)
    if not exito_validacion: 
        return crear_respuesta_error(mensaje_error)

    tipo_op_historial = "Compra" if accion == ACCION_COMPRAR else "Venta"
    exito_ejecucion, detalles_ejecucion = ejecutar_transaccion(
        billetera=billetera,
        moneda_origen=moneda_origen,
        cantidad_origen_bruta=cantidad_origen_bruta,
        moneda_destino=moneda_destino,
        tipo_operacion_historial=tipo_op_historial,
        es_orden_pendiente=False
    )

    if not exito_ejecucion:
        error_msg = detalles_ejecucion.get("error", "Error desconocido durante la ejecución.")
        return crear_respuesta_error(error_msg)

    guardar_billetera(billetera)

    resultado_operacion = {
        "titulo": "Operación de Mercado Exitosa",
        "tipo": "mercado",
        "detalles": {
            "recibiste": {"cantidad": formato_cantidad_cripto(detalles_ejecucion["cantidad_destino_final"]), "ticker": moneda_destino},
            "pagaste": {"cantidad": formato_cantidad_cripto(cantidad_origen_bruta), "ticker": moneda_origen},
            "comision": {"cantidad": formato_cantidad_cripto(detalles_ejecucion["cantidad_comision"]), "ticker": moneda_origen}
        }
    }
    return crear_respuesta_exitosa(resultado_operacion)

def _calcular_reserva_y_cantidad_principal(
    accion: str, 
    modo_ingreso: str, 
    monto_form: Decimal, 
    precio_disparo: Decimal,
    precio_destino_usdt: Decimal | None = None
) -> Dict[str, Any]:
    """
    Calcula la cantidad a reservar y la cantidad principal de la cripto para una orden pendiente.
    Es una función de cálculo pura que no realiza I/O.
    Devuelve un diccionario con el resultado.
    """
    cantidad_a_reservar = Decimal("0")
    cantidad_cripto_principal = Decimal("0")

    if accion == ACCION_COMPRAR:
        if modo_ingreso == 'monto':
            cantidad_cripto_principal = monto_form
            cantidad_a_reservar = cantidad_cripto_principal * precio_disparo
        elif modo_ingreso == 'total':
            cantidad_a_reservar = monto_form
            if precio_disparo.is_zero():
                return crear_respuesta_error("El precio de disparo no puede ser cero para este cálculo.")
            cantidad_cripto_principal = cantidad_a_reservar / precio_disparo
        else:
            return crear_respuesta_error(f"Modo de ingreso '{modo_ingreso}' no válido para una compra.")

    elif accion == ACCION_VENDER:
        if modo_ingreso == 'monto':
            cantidad_cripto_principal = monto_form
            cantidad_a_reservar = cantidad_cripto_principal
        elif modo_ingreso == 'total':
            if not precio_destino_usdt or precio_destino_usdt.is_zero():
                return crear_respuesta_error("Se requiere un precio de destino válido para este cálculo.")
            if precio_disparo.is_zero():
                return crear_respuesta_error("El precio de disparo no puede ser cero para este cálculo.")
            
            valor_usd_objetivo = monto_form * precio_destino_usdt
            cantidad_cripto_principal = valor_usd_objetivo / precio_disparo
            cantidad_a_reservar = cantidad_cripto_principal
        else:
            return crear_respuesta_error(f"Modo de ingreso '{modo_ingreso}' no válido para una venta.")
    else:
        return crear_respuesta_error(f"Acción desconocida: {accion}")

    return crear_respuesta_exitosa({
        "cantidad_a_reservar": cantidad_a_reservar,
        "cantidad_cripto_principal": cantidad_cripto_principal
    })

def _crear_orden_pendiente(moneda_origen: str, moneda_destino: str, monto_form: Decimal, modo_ingreso: str, precio_disparo: Decimal, tipo_orden: str, accion: str, precio_limite: Decimal | None) -> Dict[str, Any]:
    """Crea y guarda una orden pendiente (Límite o Stop-Limit)."""
    billetera = cargar_billetera()
    
    if precio_disparo.is_zero():
        return crear_respuesta_error("❌ El precio de disparo no puede ser cero.")

    # Obtener precio de destino si es necesario para el cálculo
    precio_destino_usdt = None
    if accion == ACCION_VENDER and modo_ingreso == 'total':
        precio_destino_usdt = obtener_precio(moneda_destino)
        if not precio_destino_usdt or precio_destino_usdt.is_zero():
            return crear_respuesta_error(f"❌ No se pudo obtener la cotización actual de {moneda_destino} para calcular la reserva.")

    # Calcular cantidades usando la nueva función de ayuda
    resultado_calculo = _calcular_reserva_y_cantidad_principal(
        accion, modo_ingreso, monto_form, precio_disparo, precio_destino_usdt
    )
    if resultado_calculo["estado"] == "error":
        mensaje = f"Error en cálculo de reserva: {resultado_calculo['mensaje']}"
        return crear_respuesta_error(mensaje)

    datos_calculo = resultado_calculo["datos"]
    cantidad_a_reservar = datos_calculo["cantidad_a_reservar"]
    cantidad_cripto_principal = datos_calculo["cantidad_cripto_principal"]
    
    moneda_a_reservar = moneda_origen

    exito_validacion, mensaje_error = _validar_saldo_disponible(billetera, moneda_a_reservar, cantidad_a_reservar)
    if not exito_validacion: 
        return crear_respuesta_error(mensaje_error)

    billetera[moneda_a_reservar]["saldos"]["disponible"] -= cantidad_a_reservar
    billetera[moneda_a_reservar]["saldos"]["reservado"] += cantidad_a_reservar
    guardar_billetera(billetera)

    id_orden = str(uuid.uuid4())
    par_correcto = f"{moneda_destino}/{moneda_origen}" if accion == ACCION_COMPRAR else f"{moneda_origen}/{moneda_destino}"

    nueva_orden = {
        "id_orden": id_orden,
        "timestamp_creacion": datetime.now().isoformat(),
        "tipo_orden": tipo_orden,
        "accion": accion,
        "par": par_correcto,
        "moneda_origen": moneda_origen,
        "moneda_destino": moneda_destino,
        "cantidad_cripto_principal": str(cuantizar_cripto(cantidad_cripto_principal)),
        "precio_disparo": str(cuantizar_usd(precio_disparo)),
        "precio_limite": str(cuantizar_usd(precio_limite)) if precio_limite else None,
        "cantidad_reservada": str(cuantizar_cripto(cantidad_a_reservar)),
        "moneda_reservada": moneda_a_reservar,
        "estado": "pendiente"
    }
    agregar_orden_pendiente(nueva_orden)
    
    accion_texto = "Compra" if accion == ACCION_COMPRAR else "Venta"
    ticker_mostrado = moneda_destino if accion == ACCION_COMPRAR else moneda_origen
    
    resultado_operacion = {
        "titulo": f"Orden {tipo_orden.replace('-', ' ').title()} Creada",
        "tipo": tipo_orden,
        "detalles": {
            "accion": f"{accion_texto} de {formato_cantidad_cripto(cantidad_cripto_principal)} {ticker_mostrado}",
            "precio_disparo": formato_cantidad_usd(precio_disparo)
        }
    }
    return crear_respuesta_exitosa(resultado_operacion)

def procesar_operacion_trading(formulario: dict) -> Dict[str, Any]:
    """Punto de entrada principal para procesar una operación desde el formulario."""
    try:
        ticker_principal = formulario["ticker"].upper()
        accion = formulario["accion"]
        monto_form = a_decimal(formulario["monto"])
        modo_ingreso = formulario.get("modo-ingreso", "monto")
        tipo_orden = formulario.get("tipo-orden", "market").lower()
    except (KeyError, ValueError) as e:
        return crear_respuesta_error(f"❌ Error en los datos del formulario: {e}")

    if monto_form <= a_decimal(0): 
        return crear_respuesta_error("❌ El monto debe ser un número positivo.")

    moneda_origen, moneda_destino = (formulario.get("moneda-pago", "USDT").upper(), ticker_principal) if accion == ACCION_COMPRAR else (ticker_principal, formulario.get("moneda-recibir", "USDT").upper())
    if moneda_origen == moneda_destino: 
        return crear_respuesta_error("❌ La moneda de origen y destino no pueden ser la misma.")

    if tipo_orden == "market":
        return _ejecutar_orden_mercado(moneda_origen, moneda_destino, monto_form, modo_ingreso, accion)
    
    elif tipo_orden in ["limit", "stop-limit"]:
        try:
            precio_disparo = a_decimal(formulario.get("precio_disparo"))
            if precio_disparo <= a_decimal(0): 
                return crear_respuesta_error("❌ Se requiere un precio de disparo válido y positivo.")
            
            precio_limite = None
            if tipo_orden == 'stop-limit':
                precio_limite = a_decimal(formulario.get("precio_limite"))
                if precio_limite <= a_decimal(0):
                    return crear_respuesta_error("❌ Se requiere un precio límite válido y positivo para una orden Stop-Limit.")

        except (KeyError, ValueError, TypeError):
            return crear_respuesta_error("❌ Precio de disparo o límite inválido o faltante.")
        
        return _crear_orden_pendiente(
            moneda_origen, 
            moneda_destino, 
            monto_form, 
            modo_ingreso, 
            precio_disparo, 
            tipo_orden, 
            accion, 
            precio_limite
        )
    
    else:
        return crear_respuesta_error(f"Tipo de orden '{tipo_orden}' no soportado.")