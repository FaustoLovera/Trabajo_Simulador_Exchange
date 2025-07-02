"""Módulo Orquestador de Operaciones de Trading.

Este módulo actúa como la fachada principal y el punto de entrada para todas
las operaciones de trading iniciadas por el usuario. Su responsabilidad es
recibir los datos crudos del formulario, validarlos, procesarlos y orquestar
la secuencia de operaciones correcta según el tipo de orden (Mercado, Límite, etc.).

El flujo de trabajo general es:
1.  **Parseo y Validación Inicial**: `procesar_operacion_trading` recibe los datos.
2.  **Dispatching**: Se deriva a la función específica según el tipo de orden.
3.  **Orquestación**: Las funciones internas (`_ejecutar_orden_mercado`,
    `_crear_orden_pendiente`) coordinan los siguientes pasos:
    a.  Cálculo de cantidades.
    b.  Validación de saldos y reglas de negocio.
    c.  Ejecución o creación de la orden (involucrando a `ejecutar_orden`).
    d.  Persistencia del estado (billetera, órdenes).
    e.  Formateo de una respuesta estandarizada para el frontend.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Tuple, Dict, Any

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
import config
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_ordenes import agregar_orden_pendiente
from backend.servicios.trading.ejecutar_orden import ejecutar_transaccion
from backend.utils.responses import crear_respuesta_error, crear_respuesta_exitosa
from backend.utils.utilidades_numericas import (
    a_decimal, cuantizar_cripto, cuantizar_usd, 
    formato_cantidad_cripto, formato_cantidad_usd
)

def _validar_saldo_disponible(
    billetera: Dict[str, Any],
    moneda_origen: str,
    cantidad_requerida: Decimal,
) -> Tuple[bool, str | None]:
    """Valida si hay suficiente saldo disponible para una operación.

    Función de validación pura que no modifica el estado.

    Args:
        billetera: El objeto de la billetera del usuario.
        moneda_origen: El ticker de la moneda de la que se gastará.
        cantidad_requerida: La cantidad necesaria para la operación.

    Returns:
        Una tupla `(es_valido, mensaje)` donde `es_valido` es `True` si hay
        saldo suficiente, y `mensaje` contiene el error si no lo hay.
    """
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
    """Calcula las cantidades brutas de un intercambio (función pura).

    Esta función no tiene efectos secundarios. Determina, a partir de la
    intención del usuario, cuánto de cada moneda está involucrado en la
    operación antes de comisiones.

    Args:
        accion: 'compra' o 'venta'.
        modo_ingreso: 'monto' (cantidad de cripto) o 'total' (cantidad de fiat).
        monto_form: El valor numérico ingresado por el usuario.
        precio_origen_usdt: Precio en USDT de la moneda de origen.
        precio_destino_usdt: Precio en USDT de la moneda de destino.

    Returns:
        Una tupla `(exito, resultado)` donde `resultado` es un diccionario
        con las cantidades calculadas o un string con un mensaje de error.
    """
    if precio_origen_usdt.is_zero() or precio_destino_usdt.is_zero():
        return False, "No se pudo obtener una cotización válida para el par."

    cantidad_origen_bruta = Decimal("0")
    cantidad_destino_bruta = Decimal("0")
    valor_usd = Decimal("0")
    
    if accion == config.ACCION_COMPRAR:
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
    
    elif accion == config.ACCION_VENDER:
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
    
def _ejecutar_orden_mercado(
    moneda_origen: str,
    moneda_destino: str,
    monto_form: Decimal,
    modo_ingreso: str,
    accion: str,
) -> Dict[str, Any]:
    """Orquesta la ejecución completa de una orden de mercado.

    Pipeline de ejecución:
    1.  Obtiene cotizaciones actuales.
    2.  Calcula las cantidades brutas del intercambio.
    3.  Carga la billetera y valida el saldo disponible.
    4.  Invoca a `ejecutar_transaccion` para la operación atómica.
    5.  Si tiene éxito, persiste el nuevo estado de la billetera.
    6.  Formatea y devuelve una respuesta para el frontend.

    Args:
        moneda_origen: Ticker de la moneda a gastar.
        moneda_destino: Ticker de la moneda a recibir.
        monto_form: La cantidad ingresada en el formulario.
        modo_ingreso: 'monto' o 'total'.
        accion: 'compra' o 'venta'.

    Returns:
        Un diccionario de respuesta estándar con el resultado de la operación.
    """
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

    # Se define un tipo de operación genérico para el historial.
    tipo_op_historial = f"COMPRA-MARKET" if accion == config.ACCION_COMPRAR else f"VENTA-MARKET"

    # Se invoca al kernel transaccional para ejecutar la operación.
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

    # Si la ejecución fue exitosa, se persiste el estado final de la billetera.
    guardar_billetera(billetera)

    # Se formatea una respuesta de éxito para el frontend.
    resultado_operacion = {
        "titulo": "Operación de Mercado Exitosa",
        "tipo": "mercado",
        "detalles": {
            "recibiste": {
                "cantidad": formato_cantidad_cripto(
                    detalles_ejecucion["cantidad_destino_final"]
                ),
                "ticker": moneda_destino,
            },
            "pagaste": {
                "cantidad": formato_cantidad_cripto(cantidad_origen_bruta),
                "ticker": moneda_origen,
            },
            "comision": {
                "cantidad": formato_cantidad_cripto(
                    detalles_ejecucion["cantidad_comision"]
                ),
                "ticker": moneda_origen,
            },
        },
    }
    return crear_respuesta_exitosa(resultado_operacion)

def _calcular_reserva_y_cantidad_principal(
    accion: str,
    modo_ingreso: str,
    monto_form: Decimal,
    precio_disparo: Decimal,
    precio_destino_usdt: Decimal | None = None,
) -> Dict[str, Any]:
    """Calcula la cantidad a reservar para una orden pendiente (función pura).

    Determina qué moneda y qué cantidad de esa moneda debe ser reservada
    para garantizar la futura ejecución de una orden Límite o Stop.

    Args:
        accion: 'compra' o 'venta'.
        modo_ingreso: 'monto' o 'total'.
        monto_form: Valor del formulario.
        precio_disparo: Precio al que se activará la orden.
        precio_destino_usdt: Requerido para ciertos cálculos de venta.

    Returns:
        Un diccionario de respuesta estándar con `cantidad_a_reservar` y
        `cantidad_cripto_principal`.
    """
    cantidad_a_reservar = Decimal("0")
    cantidad_cripto_principal = Decimal("0")

    if accion == config.ACCION_COMPRAR:
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

    elif accion == config.ACCION_VENDER:
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

def _crear_orden_pendiente(
    billetera: Dict[str, Any],
    moneda_origen: str,
    moneda_destino: str,
    monto_form: Decimal,
    modo_ingreso: str,
    precio_disparo: Decimal,
    tipo_orden: str,
    accion: str,
    precio_limite: Decimal | None,
) -> Tuple[bool, Dict[str, Any]]:
    """Prepara y valida una orden pendiente, y actualiza la billetera en memoria.

    Esta función es una operación pura en el sentido de que no realiza I/O (no lee
    ni escribe en disco). Recibe el estado de la billetera, realiza todos los
    cálculos y validaciones, y si todo es correcto, devuelve la nueva orden y
    el estado modificado de la billetera. La persistencia es responsabilidad
    del llamador.

    Retorna:
        Una tupla (éxito, resultado), donde resultado es un diccionario con
        la nueva orden y la billetera modificada, o un diccionario de error.
    """
    precio_destino_usdt = obtener_precio(moneda_destino)
    respuesta_calculo = _calcular_reserva_y_cantidad_principal(accion, modo_ingreso, monto_form, precio_disparo, precio_destino_usdt)
    if respuesta_calculo["estado"] == config.ESTADO_ERROR:
        return False, {"error": respuesta_calculo["error"]}

    datos_calculo = respuesta_calculo["datos"]
    cantidad_a_reservar = datos_calculo["cantidad_a_reservar"]
    cantidad_cripto_principal = datos_calculo["cantidad_cripto_principal"]

    exito_validacion, mensaje_error = _validar_saldo_disponible(billetera, moneda_origen, cantidad_a_reservar)
    if not exito_validacion:
        return False, {"error": mensaje_error}

    # Reservar fondos (modifica la billetera en memoria)
    billetera[moneda_origen]['saldos']['disponible'] -= cantidad_a_reservar
    billetera[moneda_origen]['saldos']['reservado'] += cantidad_a_reservar

    # Crear el objeto de la nueva orden
    par = f"{moneda_destino}/{moneda_origen}" if accion == config.ACCION_COMPRAR else f"{moneda_origen}/{moneda_destino}"
    id_orden = f"{par.replace('/', '_').lower()}_{str(uuid.uuid4())[:8]}"

    nueva_orden = {
        "id_orden": id_orden,
        "par": par,
        "accion": accion,
        "tipo_orden": tipo_orden,
        "cantidad": str(cuantizar_cripto(cantidad_cripto_principal)),
        "precio_limite": str(cuantizar_usd(precio_limite)) if precio_limite else "0",
        "precio_disparo": str(cuantizar_usd(precio_disparo)),
        "moneda_reservada": moneda_origen,
        "cantidad_reservada": str(cuantizar_usd(cantidad_a_reservar) if moneda_origen == 'USDT' else cuantizar_cripto(cantidad_a_reservar)),
        "estado": config.ESTADO_PENDIENTE,
        "timestamp_creacion": datetime.now().isoformat(),
    }

    return True, {"orden": nueva_orden, "billetera": billetera}

def procesar_operacion_trading(formulario: Dict[str, Any]) -> Dict[str, Any]:
    """Punto de entrada principal para procesar una operación desde el formulario.

    Esta función actúa como un controlador que parsea, valida y despacha la
    solicitud de trading a la función de orquestación correspondiente.

    Args:
        formulario: Un diccionario con los datos crudos del formulario de trading.

    Returns:
        Un diccionario de respuesta estándar para ser enviado como JSON al frontend.
    """
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

    moneda_origen, moneda_destino = (formulario.get("moneda-pago", "USDT").upper(), ticker_principal) if accion == config.ACCION_COMPRAR else (ticker_principal, formulario.get("moneda-recibir", "USDT").upper())
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

                # --- LÓGICA DE VALIDACIÓN AÑADIDA ---
                precio_mercado_actual = obtener_precio(ticker_principal)
                if not precio_mercado_actual:
                    return crear_respuesta_error(f"❌ No se pudo obtener el precio actual de {ticker_principal} para validar la orden.")

                if accion == config.ACCION_COMPRAR:
                    # Para una compra Stop (Buy Stop), el precio Stop DEBE estar POR ENCIMA del precio de mercado.
                    if precio_disparo <= precio_mercado_actual:
                        return crear_respuesta_error(f"❌ Para una Compra Stop, el Precio Stop ({precio_disparo}) debe ser mayor al precio actual ({precio_mercado_actual}).")
                    # El precio límite es el precio MÁXIMO que estás dispuesto a pagar. Debe ser >= al Stop.
                    if precio_limite < precio_disparo:
                        return crear_respuesta_error(f"❌ Para una Compra Stop-Limit, el Precio Límite ({precio_limite}) no puede ser menor al Precio Stop ({precio_disparo}).")

                elif accion == config.ACCION_VENDER:
                    # Para una venta Stop (Sell Stop), el precio Stop DEBE estar POR DEBAJO del precio de mercado.
                    if precio_disparo >= precio_mercado_actual:
                        return crear_respuesta_error(f"❌ Para una Venta Stop, el Precio Stop ({precio_disparo}) debe ser menor al precio actual ({precio_mercado_actual}).")
                    # El precio límite es el precio MÍNIMO al que estás dispuesto a vender. Debe ser <= al Stop.
                    if precio_limite > precio_disparo:
                        return crear_respuesta_error(f"❌ Para una Venta Stop-Limit, el Precio Límite ({precio_limite}) no puede ser mayor al Precio Stop ({precio_disparo}).")
                # --- FIN DE LA LÓGICA DE VALIDACIÓN ---

        except (KeyError, ValueError, TypeError):
            return crear_respuesta_error("❌ Precio de disparo o límite inválido o faltante.")
        
        # El resto de la llamada no cambia
        billetera = cargar_billetera()
        exito, resultado = _crear_orden_pendiente(
            billetera=billetera,
            moneda_origen=moneda_origen,
            moneda_destino=moneda_destino,
            monto_form=monto_form,
            modo_ingreso=modo_ingreso,
            precio_disparo=precio_disparo,
            tipo_orden=tipo_orden,
            accion=accion,
            precio_limite=precio_limite
        )

        if not exito:
            return crear_respuesta_error(resultado.get("error", "Error desconocido al crear orden pendiente."))

        # Persistencia
        nueva_orden = resultado["orden"]
        billetera_modificada = resultado["billetera"]
        guardar_billetera(billetera_modificada)
        agregar_orden_pendiente(nueva_orden)

        # Formateo de respuesta para el frontend
        resultado_operacion = {
            "titulo": "Orden Pendiente Creada",
            "tipo": tipo_orden,
            "detalles": {
                "id_orden": nueva_orden["id_orden"],
                "par": nueva_orden["par"],
                "accion": nueva_orden["accion"],
                "cantidad": formato_cantidad_cripto(a_decimal(nueva_orden["cantidad"])),
                "precio_disparo": formato_cantidad_usd(a_decimal(nueva_orden["precio_disparo"])),
                "precio_limite": formato_cantidad_usd(a_decimal(nueva_orden["precio_limite"])) if precio_limite else "N/A",
            }
        }
        return crear_respuesta_exitosa(resultado_operacion)
    
    else:
        return crear_respuesta_error(f"Tipo de orden '{tipo_orden}' no soportado.")