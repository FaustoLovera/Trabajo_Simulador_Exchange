# backend/servicios/trading/procesador.py

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Tuple, Dict, Any

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio, cargar_datos_cotizaciones
from backend.acceso_datos.datos_ordenes import agregar_orden_pendiente
from backend.servicios.trading.ejecutar_orden import ejecutar_transaccion
from backend.utils.utilidades_numericas import a_decimal, cuantizar_cripto, cuantizar_usd, formato_cantidad_cripto, formato_cantidad_usd

# --- Las funciones _validar_saldo_disponible, _calcular_detalles_intercambio y _ejecutar_orden_mercado no cambian ---

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
    
    # Lógica para COMPRAR (sin cambios)
    if accion == "comprar":
        if modo_ingreso == "monto":
            # El usuario especifica la cantidad de CRIPTO que quiere recibir.
            # Ejemplo: Comprar 0.5 BTC.
            cantidad_destino_bruta = monto_form
            valor_usd = cantidad_destino_bruta * precio_destino_usdt
            cantidad_origen_bruta = valor_usd / precio_origen_usdt
        elif modo_ingreso == "total":
            # El usuario especifica la cantidad de FIAT/PAGO que quiere gastar.
            # Ejemplo: Comprar $100 de BTC.
            cantidad_origen_bruta = monto_form
            valor_usd = cantidad_origen_bruta * precio_origen_usdt
            cantidad_destino_bruta = valor_usd / precio_destino_usdt
        else:
            return False, f"Modo de ingreso '{modo_ingreso}' no válido para una compra."
    
    # Lógica para VENDER (¡MODIFICADA Y FLEXIBLE!)
    elif accion == "vender":
        if modo_ingreso == "monto":
            # El usuario especifica la cantidad de CRIPTO que quiere vender.
            # Ejemplo: Vender 1000 XLM.
            cantidad_origen_bruta = monto_form
            valor_usd = cantidad_origen_bruta * precio_origen_usdt
            cantidad_destino_bruta = valor_usd / precio_destino_usdt
        elif modo_ingreso == "total":
            # El usuario especifica la cantidad de la MONEDA DESTINO que quiere recibir.
            # Ejemplo: Vender XLM para obtener exactamente 1 BNB.
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
    
def _ejecutar_orden_mercado(moneda_origen: str, moneda_destino: str, monto_form: Decimal, modo_ingreso: str, accion: str) -> Tuple[bool, Dict[str, Any] | str]:
    """
    Orquesta la ejecución de una orden a precio de mercado.
    Delega la transacción final al módulo 'ejecutor'.
    """
    precio_origen_usdt = obtener_precio(moneda_origen)
    precio_destino_usdt = obtener_precio(moneda_destino)
    if not all([precio_origen_usdt, precio_destino_usdt]):
        return False, "❌ No se pudo obtener la cotización para realizar el swap."

    exito_calculo, detalles_brutos = _calcular_detalles_intercambio(accion, modo_ingreso, monto_form, precio_origen_usdt, precio_destino_usdt)
    if not exito_calculo:
        return False, f"❌ {detalles_brutos}"

    cantidad_origen_bruta = detalles_brutos["cantidad_origen_bruta"]
    billetera = cargar_billetera()
    exito_validacion, mensaje_error = _validar_saldo_disponible(billetera, moneda_origen, cantidad_origen_bruta)
    if not exito_validacion: 
        return False, mensaje_error

    tipo_op_historial = "Compra" if accion == "comprar" else "Venta"
    exito_ejecucion, detalles_ejecucion = ejecutar_transaccion(
        billetera=billetera,
        moneda_origen=moneda_origen,
        cantidad_origen_bruta=cantidad_origen_bruta,
        moneda_destino=moneda_destino,
        tipo_operacion_historial=tipo_op_historial,
        es_orden_pendiente=False
    )

    if not exito_ejecucion:
        return False, detalles_ejecucion.get("error", "Error desconocido durante la ejecución.")

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
    return True, resultado_operacion

# --- CAMBIO PRINCIPAL EN EL BACKEND ---
# Añadimos 'modo_ingreso' para que la función sea más inteligente.
def _crear_orden_pendiente(moneda_origen: str, moneda_destino: str, monto_form: Decimal, modo_ingreso: str, precio_disparo: Decimal, tipo_orden: str, accion: str) -> Tuple[bool, Dict[str, Any] | str]:
    billetera = cargar_billetera()
    
    # Valida que el precio de disparo no sea cero para evitar divisiones por cero.
    if precio_disparo.is_zero():
        return False, "❌ El precio de disparo no puede ser cero."

    # --- LÓGICA DE COMPRA (SIN CAMBIOS, YA ERA FLEXIBLE) ---
    if accion == 'comprar':
        moneda_a_reservar = moneda_origen # Se reserva USDT (o la moneda de pago)
        if modo_ingreso == 'monto':
            # Usuario quiere comprar una cantidad FIJA de cripto (destino).
            # Ejemplo: Comprar 0.5 BTC cuando el precio llegue a $40,000.
            cantidad_cripto_principal = monto_form
            cantidad_a_reservar = cantidad_cripto_principal * precio_disparo
        elif modo_ingreso == 'total':
            # Usuario quiere gastar una cantidad FIJA de la moneda de pago.
            # Ejemplo: Comprar $20,000 de BTC cuando el precio llegue a $40,000.
            cantidad_a_reservar = monto_form
            cantidad_cripto_principal = cantidad_a_reservar / precio_disparo
        else:
            return False, f"Modo de ingreso '{modo_ingreso}' no válido para una compra límite."

    # --- LÓGICA DE VENTA (¡MODIFICADA Y FLEXIBLE!) ---
    elif accion == 'vender':
        moneda_a_reservar = moneda_origen # Se reserva la cripto que se vende (ej: XLM)
        
        if modo_ingreso == 'monto':
            # Usuario quiere vender una cantidad FIJA de la cripto (origen).
            # Ejemplo: Vender 1000 XLM cuando el precio llegue a $0.30.
            cantidad_cripto_principal = monto_form
            cantidad_a_reservar = cantidad_cripto_principal
        
        elif modo_ingreso == 'total':
            # Usuario quiere recibir una cantidad FIJA de la moneda destino.
            # Ejemplo: Vender XLM para obtener 1 BNB, cuando el precio de XLM llegue a $0.30.
            # Necesitamos el precio de la moneda destino para hacer la conversión.
            precio_destino_usdt = obtener_precio(moneda_destino)
            if not precio_destino_usdt or precio_destino_usdt.is_zero():
                return False, f"❌ No se pudo obtener la cotización actual de {moneda_destino} para calcular la reserva."

            # 1. Calcula el valor total en USD de lo que se quiere recibir.
            valor_usd_objetivo = monto_form * precio_destino_usdt
            # 2. Calcula cuánta cripto principal se necesitaría vender a PRECIO DE DISPARO.
            cantidad_cripto_principal = valor_usd_objetivo / precio_disparo
            cantidad_a_reservar = cantidad_cripto_principal
        else:
            return False, f"Modo de ingreso '{modo_ingreso}' no válido para una venta límite."
    else:
        return False, f"Acción desconocida: {accion}"

    # El resto de la función (validación de saldo, reserva y creación de orden) no cambia
    exito_validacion, mensaje_error = _validar_saldo_disponible(billetera, moneda_a_reservar, cantidad_a_reservar)
    if not exito_validacion: 
        return False, mensaje_error

    billetera[moneda_a_reservar]["saldos"]["disponible"] -= cantidad_a_reservar
    billetera[moneda_a_reservar]["saldos"]["reservado"] += cantidad_a_reservar
    guardar_billetera(billetera)

    nueva_orden = {
        "id_orden": str(uuid.uuid4()),
        "timestamp_creacion": datetime.now().isoformat(),
        "tipo_orden": tipo_orden,
        "accion": accion,
        "par": f"{moneda_origen}/{moneda_destino}",
        "moneda_origen": moneda_origen,
        "moneda_destino": moneda_destino,
        "cantidad_cripto_principal": str(cuantizar_cripto(cantidad_cripto_principal)),
        "precio_disparo": str(cuantizar_usd(precio_disparo)),
        "cantidad_reservada": str(cuantizar_cripto(cantidad_a_reservar)),
        "moneda_reservada": moneda_a_reservar,
        "estado": "pendiente"
    }
    agregar_orden_pendiente(nueva_orden)
    
    accion_texto = "Compra" if accion == 'comprar' else "Venta"
    ticker_mostrado = moneda_destino if accion == 'comprar' else moneda_origen
    
    resultado_operacion = {
        "titulo": f"Orden {tipo_orden.capitalize()} Creada",
        "tipo": tipo_orden,
        "detalles": {
            "accion": f"{accion_texto} de {formato_cantidad_cripto(cantidad_cripto_principal)} {ticker_mostrado}",
            "precio_disparo": formato_cantidad_usd(precio_disparo)
        }
    }
    return True, resultado_operacion


def procesar_operacion_trading(formulario: dict) -> Tuple[bool, Dict[str, Any] | str]:
    try:
        ticker_principal = formulario["ticker"].upper()
        accion = formulario["accion"]
        # Este es el 'monto-final' que envía el frontend
        monto_form = a_decimal(formulario["monto"])
        # Este es el 'modo-ingreso-final'
        modo_ingreso = formulario.get("modo-ingreso", "monto")
        tipo_orden = formulario.get("tipo-orden", "market").lower()
    except (KeyError, ValueError) as e:
        return False, f"❌ Error en los datos del formulario: {e}"

    if monto_form <= a_decimal(0): return False, "❌ El monto debe ser un número positivo."

    moneda_origen, moneda_destino = (formulario.get("moneda-pago", "USDT").upper(), ticker_principal) if accion == "comprar" else (ticker_principal, formulario.get("moneda-recibir", "USDT").upper())
    if moneda_origen == moneda_destino: return False, "❌ La moneda de origen y destino no pueden ser la misma."

    if tipo_orden == "market":
        return _ejecutar_orden_mercado(moneda_origen, moneda_destino, monto_form, modo_ingreso, accion)
    
    elif tipo_orden in ["limit", "stop-loss"]:
        try:
            precio_disparo = a_decimal(formulario.get("precio_disparo"))
            if precio_disparo <= a_decimal(0): 
                return False, "❌ Se requiere un precio de disparo válido y positivo."
        except (KeyError, ValueError):
            return False, "❌ Precio de disparo inválido o faltante."
        
        # Le pasamos el 'modo_ingreso' a la función de crear orden pendiente
        return _crear_orden_pendiente(moneda_origen, moneda_destino, monto_form, modo_ingreso, precio_disparo, tipo_orden, accion)
    
    return False, f"❌ Tipo de orden desconocido: '{tipo_orden}'."