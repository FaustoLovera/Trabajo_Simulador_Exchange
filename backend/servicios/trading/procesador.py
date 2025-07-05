"""Módulo Orquestador de Operaciones de Trading.

Este módulo actúa como la fachada principal y el punto de entrada para todas
las operaciones de trading iniciadas por el usuario. Su responsabilidad es
recibir los datos crudos del formulario, validarlos, procesarlos y orquestar
la secuencia de operaciones correcta según el tipo de orden (Mercado, Límite, etc.).

El flujo de trabajo general es:
1.  **Parseo y Validación Inicial**: `procesar_operacion_trading` recibe los datos.
2.  **Dispatching**: Se deriva a la función específica según el tipo de orden.
3.  **Orquestación**: Las funciones internas coordinan los siguientes pasos:
    a.  Cálculo de cantidades.
    b.  Validación de saldos y reglas de negocio.
    c.  Ejecución o creación de la orden (invocando a la fábrica de órdenes).
    d.  Persistencia del estado (billetera, órdenes).
    e.  Formateo de una respuesta estandarizada para el frontend.
"""

from decimal import Decimal
from typing import Tuple, Dict, Any

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
import config
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_ordenes import agregar_orden_pendiente
from backend.servicios.trading.ejecutar_orden import ejecutar_transaccion
from backend.servicios.trading.motor import _crear_nueva_orden
from backend.utils.responses import crear_respuesta_error, crear_respuesta_exitosa
from backend.utils.utilidades_numericas import a_decimal, formato_cantidad_cripto, formato_cantidad_usd

def _validar_saldo_disponible(
    billetera: Dict[str, Any],
    moneda_origen: str,
    cantidad_requerida: Decimal,
) -> Tuple[bool, str | None]:
    
    """Valida si hay suficiente saldo disponible para una operación."""
    
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
    precio_destino_usdt: Decimal,
) -> Tuple[bool, Dict[str, Any] | str]:
    """Calcula las cantidades brutas de un intercambio (función pura)."""
    if precio_origen_usdt.is_zero() or precio_destino_usdt.is_zero():
        return False, "No se pudo obtener una cotización válida para el par."

    cantidad_origen_bruta = Decimal("0")
    valor_usd = Decimal("0")
    
    if accion == config.ACCION_COMPRAR:
        if modo_ingreso == "monto":
            cantidad_destino_bruta = monto_form
            valor_usd = cantidad_destino_bruta * precio_destino_usdt
            cantidad_origen_bruta = valor_usd / precio_origen_usdt
        elif modo_ingreso == "total":
            cantidad_origen_bruta = monto_form
            valor_usd = cantidad_origen_bruta * precio_origen_usdt
        else:
            return False, f"Modo de ingreso '{modo_ingreso}' no válido para una compra."
    
    elif accion == config.ACCION_VENDER:
        if modo_ingreso == "monto":
            cantidad_origen_bruta = monto_form
            valor_usd = cantidad_origen_bruta * precio_origen_usdt
        elif modo_ingreso == "total":
            valor_usd = monto_form
            cantidad_origen_bruta = valor_usd / precio_origen_usdt
        else:
            return False, f"Modo de ingreso '{modo_ingreso}' no válido para una venta."
    else:
        return False, f"Acción de trading desconocida: '{accion}'."

    return True, {"cantidad_origen_bruta": cantidad_origen_bruta, "valor_usd": valor_usd}

def _ejecutar_orden_mercado(
    moneda_origen: str,
    moneda_destino: str,
    monto_form: Decimal,
    modo_ingreso: str,
    accion: str,
) -> Dict[str, Any]:
    """Orquesta la ejecución completa de una orden de mercado."""
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

    tipo_orden_str = config.TIPO_ORDEN_MERCADO.upper()
    accion_str = accion.upper()
    tipo_op_historial = f"{tipo_orden_str}-{accion_str}"

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
        "tipo": config.TIPO_ORDEN_MERCADO,
        "detalles": {
            "recibiste": {"cantidad": formato_cantidad_cripto(detalles_ejecucion["cantidad_destino_final"]), "ticker": moneda_destino},
            "pagaste": {"cantidad": formato_cantidad_cripto(cantidad_origen_bruta), "ticker": moneda_origen},
            "comision": {"cantidad": formato_cantidad_cripto(detalles_ejecucion["cantidad_comision"]), "ticker": moneda_origen},
        },
    }
    return crear_respuesta_exitosa(resultado_operacion)

def _calcular_reserva_y_cantidad_principal(
    accion: str,
    modo_ingreso: str,
    monto_form: Decimal,
    precio_referencia: Decimal,
) -> Dict[str, Any]:
    """Calcula la cantidad a reservar y la cantidad principal de la cripto."""
    if precio_referencia.is_zero():
        return crear_respuesta_error("El precio de referencia no puede ser cero.")

    if accion == config.ACCION_COMPRAR:
        if modo_ingreso == 'monto':
            cantidad_cripto_principal = monto_form
            cantidad_a_reservar = cantidad_cripto_principal * precio_referencia
        elif modo_ingreso == 'total':
            cantidad_a_reservar = monto_form
            cantidad_cripto_principal = cantidad_a_reservar / precio_referencia
        else:
            return crear_respuesta_error(f"Modo de ingreso '{modo_ingreso}' no válido.")
            
    elif accion == config.ACCION_VENDER:
        if modo_ingreso == 'monto':
            cantidad_cripto_principal = monto_form
            cantidad_a_reservar = cantidad_cripto_principal
        elif modo_ingreso == 'total':
            cantidad_cripto_principal = monto_form / precio_referencia
            cantidad_a_reservar = cantidad_cripto_principal
        else:
            return crear_respuesta_error(f"Modo de ingreso '{modo_ingreso}' no válido.")
    else:
        return crear_respuesta_error(f"Acción desconocida: {accion}")

    return crear_respuesta_exitosa({
        "cantidad_a_reservar": cantidad_a_reservar,
        "cantidad_cripto_principal": cantidad_cripto_principal
    })

def procesar_operacion_trading(formulario: Dict[str, Any]) -> Dict[str, Any]:
    """Punto de entrada principal para procesar una operación desde el formulario."""
    # --- 1. PARSEO Y VALIDACIÓN INICIAL UNIFICADA ---
    try:
        ticker_principal = formulario.get("ticker", "").upper()
        accion = formulario.get("accion")
        monto_form = a_decimal(formulario.get("monto"))
        modo_ingreso = formulario.get("modo-ingreso", "monto")
        tipo_orden = formulario.get("tipo-orden", config.TIPO_ORDEN_MERCADO).lower()
        precio_disparo = a_decimal(formulario.get("precio_disparo"))
        precio_limite = a_decimal(formulario.get("precio_limite"))
        
        if not all([ticker_principal, accion, monto_form]):
             raise ValueError("Faltan datos esenciales en el formulario (ticker, accion, monto).")

    except (ValueError, TypeError) as e:
        return crear_respuesta_error(f"❌ Error en los datos del formulario: {e}")

    if monto_form <= Decimal("0"):
        return crear_respuesta_error("❌ El monto debe ser un número positivo.")

    # --- LÓGICA DE ASIGNACIÓN DE MONEDAS (CORREGIDA) ---
    if accion == config.ACCION_COMPRAR:
        moneda_origen = formulario.get("moneda-pago", config.MONEDA_FIAT_DEFAULT)
        moneda_destino = ticker_principal
    elif accion == config.ACCION_VENDER:
        moneda_origen = ticker_principal
        moneda_destino = formulario.get("moneda-recibir", config.MONEDA_FIAT_DEFAULT)
    else:
        return crear_respuesta_error(f"Acción de trading desconocida: '{accion}'")

    if moneda_origen == moneda_destino:
        return crear_respuesta_error("❌ La moneda de origen y destino no pueden ser la misma.")

    # --- 2. DISPATCHING POR TIPO DE ORDEN ---
    if tipo_orden == config.TIPO_ORDEN_MERCADO:
        return _ejecutar_orden_mercado(moneda_origen, moneda_destino, monto_form, modo_ingreso, accion)
    
    elif tipo_orden in [config.TIPO_ORDEN_LIMITE, config.TIPO_ORDEN_STOP_LIMIT]:
        # --- 3. LÓGICA PARA ÓRDENES PENDIENTES ---
        
        # Para órdenes 'limit' simples, el precio límite y el de disparo son conceptualmente el mismo.
        if tipo_orden == config.TIPO_ORDEN_LIMITE:
            precio_limite = precio_disparo

        # Validación de precios
        if precio_disparo <= 0:
            return crear_respuesta_error("❌ Se requiere un precio de disparo válido y positivo.")
        if tipo_orden == config.TIPO_ORDEN_STOP_LIMIT and precio_limite <= 0:
            return crear_respuesta_error("❌ Se requiere un precio límite válido y positivo para una orden Stop-Limit.")

        # Validación de precios Stop-Limit contra el precio de mercado actual
        precio_mercado_actual = obtener_precio(ticker_principal)
        if tipo_orden == config.TIPO_ORDEN_STOP_LIMIT and precio_mercado_actual:
            if accion == config.ACCION_COMPRAR:
                if precio_disparo <= precio_mercado_actual:
                    return crear_respuesta_error(f"❌ Compra Stop: Precio Stop ({formato_cantidad_usd(precio_disparo)}) debe ser > al precio actual ({formato_cantidad_usd(precio_mercado_actual)}).")
                if precio_limite < precio_disparo:
                    return crear_respuesta_error(f"❌ Compra Stop-Limit: Precio Límite ({formato_cantidad_usd(precio_limite)}) no puede ser < al Precio Stop ({formato_cantidad_usd(precio_disparo)}).")
            elif accion == config.ACCION_VENDER:
                if precio_disparo >= precio_mercado_actual:
                    return crear_respuesta_error(f"❌ Venta Stop: Precio Stop ({formato_cantidad_usd(precio_disparo)}) debe ser < al precio actual ({formato_cantidad_usd(precio_mercado_actual)}).")
                if precio_limite > precio_disparo:
                    return crear_respuesta_error(f"❌ Venta Stop-Limit: Precio Límite ({formato_cantidad_usd(precio_limite)}) no puede ser > al Precio Stop ({formato_cantidad_usd(precio_disparo)}).")
        
        # Para órdenes límite, la reserva siempre se calcula contra el precio límite.
        precio_referencia = precio_limite if tipo_orden == config.TIPO_ORDEN_STOP_LIMIT else precio_disparo
        
        # Cálculo de cantidades y reserva
        respuesta_calculo = _calcular_reserva_y_cantidad_principal(accion, modo_ingreso, monto_form, precio_referencia)
        if respuesta_calculo["estado"] == config.ESTADO_ERROR:
            return crear_respuesta_error(respuesta_calculo["mensaje"])

        datos_calculo = respuesta_calculo["datos"]
        cantidad_a_reservar = datos_calculo["cantidad_a_reservar"]
        cantidad_cripto_principal = datos_calculo["cantidad_cripto_principal"]

        # Validación de saldo y modificación de billetera
        billetera = cargar_billetera()
        exito_validacion, mensaje_error = _validar_saldo_disponible(billetera, moneda_origen, cantidad_a_reservar)
        if not exito_validacion:
            return crear_respuesta_error(mensaje_error)

        billetera[moneda_origen]['saldos']['disponible'] -= cantidad_a_reservar
        billetera[moneda_origen]['saldos']['reservado'] += cantidad_a_reservar

        # Creación de la orden usando la fábrica centralizada
        par_trading = f"{ticker_principal}/{config.MONEDA_FIAT_DEFAULT}"
        
        nueva_orden = _crear_nueva_orden(
            par=par_trading,
            tipo_orden=tipo_orden,
            accion=accion,
            cantidad=cantidad_cripto_principal,
            precio_limite=precio_limite,
            precio_disparo=precio_disparo
        )

        if config.ESTADO_ERROR in nueva_orden:
            # Si la fábrica falla, revertir la reserva en memoria antes de salir.
            billetera[moneda_origen]['saldos']['disponible'] += cantidad_a_reservar
            billetera[moneda_origen]['saldos']['reservado'] -= cantidad_a_reservar
            return crear_respuesta_error(nueva_orden[config.ESTADO_ERROR])
        
        # Persistencia de datos
        guardar_billetera(billetera)
        agregar_orden_pendiente(nueva_orden)

        # Respuesta para el frontend
        resultado_operacion = {
            "titulo": "Orden Pendiente Creada",
            "tipo": tipo_orden,
            "detalles": {
                "id_orden": nueva_orden["id_orden"],
                "par": nueva_orden["par"],
                "accion": nueva_orden["accion"].capitalize(),
                "cantidad": formato_cantidad_cripto(a_decimal(nueva_orden["cantidad"])),
                "precio_disparo": formato_cantidad_usd(a_decimal(nueva_orden["precio_disparo"])),
                "precio_limite": formato_cantidad_usd(a_decimal(nueva_orden["precio_limite"])) if tipo_orden == config.TIPO_ORDEN_STOP_LIMIT else "N/A",
            }
        }
        return crear_respuesta_exitosa(resultado_operacion, f"Orden {tipo_orden.capitalize()} creada exitosamente.")
    
    else:
        return crear_respuesta_error(f"Tipo de orden '{tipo_orden}' no soportado.")