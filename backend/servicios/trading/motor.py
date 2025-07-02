"""Motor Principal de Trading: Verificación y Ejecución de Órdenes.

Este módulo es el corazón del simulador de exchange. Emula el comportamiento
de un motor de coincidencias (`matching engine`), siendo responsable de:

1.  **Verificar Órdenes Pendientes**: Itera sobre todas las órdenes que no han
    sido ejecutadas ni canceladas.
2.  **Consultar Precios de Mercado**: Obtiene los precios actuales para los
    pares de las órdenes.
3.  **Disparar Órdenes**: Comprueba si el precio de mercado cumple las
    condiciones de disparo de cada orden (ej. precio <= precio_limite).
4.  **Ejecutar Transacciones**: Si una orden se dispara, orquesta su ejecución,
    lo que implica actualizar la billetera y el estado de la orden.

La función principal es `verificar_y_ejecutar_ordenes_pendientes()`, que
representa un "ciclo" o "tick" del motor.
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Tuple

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes
import config
from backend.servicios.trading.ejecutar_orden import ejecutar_transaccion
from backend.utils.utilidades_numericas import a_decimal, cuantizar_cripto


# backend/servicios/trading/motor.py

def _verificar_condicion_orden(orden: Dict[str, Any], precio_actual: Decimal) -> bool:
    """Evalúa si el precio de mercado actual cumple la condición de disparo de la orden.

    Esta es la lógica central que determina si una orden pendiente debe activarse.

    -   **Límite de Compra**: Se activa si el precio actual es MENOR O IGUAL al deseado.
    -   **Límite de Venta**: Se activa si el precio actual es MAYOR O IGUAL al deseado.
    -   **Stop-Limit de Compra**: Se activa si el precio actual es MAYOR O IGUAL al de disparo (stop).
    -   **Venta Stop-Limit**: Se activa si el precio actual es MENOR O IGUAL al de disparo (stop).

    Args:
        orden: La orden a verificar.
        precio_actual: El precio de mercado actual del par.

    Returns:
        True si la condición de disparo se cumple, False en caso contrario.
    """
    precio_disparo = a_decimal(orden["precio_disparo"])
    tipo_orden = orden.get("tipo_orden", config.TIPO_ORDEN_LIMITE)

    if tipo_orden == config.TIPO_ORDEN_LIMITE:
        if orden["accion"] == config.ACCION_COMPRAR:
            return precio_actual <= precio_disparo
        elif orden["accion"] == config.ACCION_VENDER:
            return precio_actual >= precio_disparo
        
    elif tipo_orden == config.TIPO_ORDEN_STOP_LIMIT:
        if orden["accion"] == config.ACCION_COMPRAR:
            return precio_actual >= precio_disparo
        elif orden["accion"] == config.ACCION_VENDER:
            return precio_actual <= precio_disparo

    return False


def _ejecutar_orden_pendiente(orden: Dict[str, Any], billetera: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecuta una orden disparada, actualizando la billetera y el estado de la orden.

    Esta función contiene la lógica de ejecución post-disparo. Su comportamiento
    más complejo es el manejo de órdenes Stop-Limit, que requieren una segunda
    validación contra el precio límite después de que el precio de disparo (stop)
    ha sido alcanzado.

    Args:
        orden: La orden pendiente que se va a ejecutar.
        billetera: El objeto de la billetera del usuario, que será modificado.

    Returns:
        El objeto de la billetera actualizado después de la operación.
    """
    if orden.get("tipo_orden") == config.TIPO_ORDEN_STOP_LIMIT:
        precio_limite = a_decimal(orden.get("precio_limite"))
        
        if not precio_limite or precio_limite.is_zero():
             print(f"❌ ERROR DE DATOS: Orden Stop-Limit {orden['id_orden']} no tiene precio límite válido.")
             orden["estado"] = config.ESTADO_ERROR
             return billetera
              
        # El precio de mercado se obtiene para el activo principal del par (ej: BTC en BTC/USDT)
        ticker_principal = orden["par"].split('/')[0]
        precio_actual_mercado = obtener_precio(ticker_principal)
        if not precio_actual_mercado:
             print(f"⚠️  No se pudo obtener el precio de mercado para {orden['par']} para validar el límite de la orden {orden['id_orden']}.")
             return billetera

        if orden["accion"] == config.ACCION_COMPRAR and precio_actual_mercado > precio_limite:
            print(f"🚦 ORDEN STOP-LIMIT {orden['id_orden']} DISPARADA, PERO NO EJECUTADA: Precio actual ({precio_actual_mercado}) > Precio Límite ({precio_limite}).")
            return billetera
        
        elif orden["accion"] == config.ACCION_VENDER and precio_actual_mercado < precio_limite:
            print(f"🚦 ORDEN STOP-LIMIT {orden['id_orden']} DISPARADA, PERO NO EJECUTADA: Precio actual ({precio_actual_mercado}) < Precio Límite ({precio_limite}).")
            return billetera

    moneda_origen = orden["moneda_reservada"]
    cantidad_origen_bruta = a_decimal(orden["cantidad_reservada"])
    # Corregido: La moneda de destino se saca del par, no de la propia orden directamente.
    moneda_destino = orden["par"].split('/')[0] if orden["accion"] == config.ACCION_COMPRAR else orden["par"].split('/')[1]
    
        # Crear un tipo de operación descriptivo para el historial.
    tipo_op_historial = f"{orden['tipo_orden']}-{orden['accion']}"

        # Ejecutar la transacción atómica, que maneja comisiones y saldos.
    exito_ejecucion, detalles_ejecucion = ejecutar_transaccion(
        billetera=billetera,
        moneda_origen=moneda_origen,
        cantidad_origen_bruta=cantidad_origen_bruta,
        moneda_destino=moneda_destino,
        tipo_operacion_historial=tipo_op_historial,
        es_orden_pendiente=True # ¡Importante! Para que use el saldo 'reservado'
    )
    
    if not exito_ejecucion:
        print(f"❌ ERROR al ejecutar orden pendiente {orden['id_orden']}: {detalles_ejecucion.get('error')}")
        orden.update({"estado": config.ESTADO_ERROR, "mensaje_error": detalles_ejecucion.get("error")})
        return billetera

    print(f"✅ ORDEN EJECUTADA: {orden['id_orden']} ({orden['par']})")
    orden.update({
        "estado": config.ESTADO_EJECUTADA,
        "timestamp_ejecucion": datetime.now().isoformat(),
        "cantidad_destino_final": str(cuantizar_cripto(detalles_ejecucion["cantidad_destino_final"]))
    })
    return billetera


def verificar_y_ejecutar_ordenes_pendientes() -> None:
    """Ciclo principal del motor: verifica y ejecuta todas las órdenes pendientes.

    Esta función representa un "tick" o ciclo completo del motor de trading.
    Orquesta el proceso de extremo a extremo:
    1.  Carga todas las órdenes y filtra las que están 'pendientes'.
    2.  Carga la billetera para poder modificarla.
    3.  Itera sobre cada orden pendiente:
        a. Obtiene el precio de mercado actual para el par de la orden.
        b. Llama a `_verificar_condicion_orden` para ver si se dispara.
        c. Si se dispara, llama a `_ejecutar_orden_pendiente`.
    4.  Persiste el estado final de las órdenes y la billetera en el almacenamiento.
    """
    todas_las_ordenes = cargar_ordenes_pendientes()
    ordenes_pendientes = [o for o in todas_las_ordenes if o.get("estado") == config.ESTADO_PENDIENTE]
    if not ordenes_pendientes: 
        return

    billetera = cargar_billetera()
    ordenes_modificadas = []
    
    for orden in ordenes_pendientes:
        # El precio de mercado se obtiene para el activo principal del par (ej: BTC en BTC/USDT)
        ticker_principal = orden["par"].split('/')[0]
        precio_actual = obtener_precio(ticker_principal)
        if not precio_actual:
            print(f"⚠️  No se pudo obtener precio para el par {orden['par']}. Saltando orden {orden['id_orden']}.")
            continue

        if _verificar_condicion_orden(orden, precio_actual):
            print(f"🔔 CONDICIÓN CUMPLIDA para orden {orden['id_orden']}. Intentando ejecutar...")
            billetera = _ejecutar_orden_pendiente(orden, billetera)
        
        ordenes_modificadas.append(orden)

    ordenes_no_modificadas = [o for o in todas_las_ordenes if o.get("estado") != config.ESTADO_PENDIENTE]
    
    guardar_ordenes_pendientes(ordenes_no_modificadas + ordenes_modificadas)
    guardar_billetera(billetera)
    print("--- Ciclo de motor de trading finalizado ---")


def _crear_nueva_orden(
    par: str,
    tipo_orden: str,
    accion: str,
    cantidad: Decimal,
    precio_limite: Decimal | None = None,
    precio_disparo: Decimal | None = None,
) -> Dict[str, Any]:
    """Función de fábrica para construir el objeto de una nueva orden.

    Esta es una función pura que valida los datos de entrada y construye el
    diccionario que representa una orden. No tiene efectos secundarios (no guarda
    nada en disco ni modifica la billetera).

    Calcula la `cantidad_reservada` y `moneda_reservada` basándose en la lógica
    de negocio para cada tipo de orden y acción.

    Args:
        par: Par de trading (ej. "BTC/USDT").
        tipo_orden: Tipo de orden ('market', 'limit', etc.).
        accion: 'compra' o 'venta'.
        cantidad: Cantidad de la moneda base a operar.
        precio_limite: Precio límite para la orden.
        precio_disparo: Precio de disparo para la orden.

    Returns:
        Un diccionario representando la nueva orden o un diccionario de error.
    """
    if tipo_orden not in [config.TIPO_ORDEN_MERCADO, config.TIPO_ORDEN_LIMITE, config.TIPO_ORDEN_STOP_LIMIT]:
        return {config.ESTADO_ERROR: "Tipo de orden no válido"}
    
    if accion not in [config.ACCION_COMPRAR, config.ACCION_VENDER]:
        return {config.ESTADO_ERROR: "Acción no válida"}

    if tipo_orden in [config.TIPO_ORDEN_LIMITE, config.TIPO_ORDEN_STOP_LIMIT] and (not precio_limite or precio_limite <= 0):
        return {config.ESTADO_ERROR: "El precio límite es obligatorio para órdenes límite y stop-limit"}

    if tipo_orden == config.TIPO_ORDEN_STOP_LIMIT and (not precio_disparo or precio_disparo <= 0):
        return {config.ESTADO_ERROR: "El precio de disparo es obligatorio para órdenes stop-limit"}

    moneda_principal, moneda_cotizada = par.split('/')
    
    if accion == config.ACCION_COMPRAR:
        moneda_reservada = moneda_cotizada
        cantidad_reservada = cantidad if tipo_orden == config.TIPO_ORDEN_MERCADO else cantidad * precio_limite
    else: # Vender
        moneda_reservada = moneda_principal
        cantidad_reservada = cantidad

    id_orden = f"{par.replace('/', '_').lower()}_{accion}_{datetime.now().timestamp()}"
    
    precio_disparo_final = precio_disparo if precio_disparo else precio_limite

    nueva_orden = {
        "id_orden": id_orden,
        "par": par,
        "accion": accion,
        "tipo_orden": tipo_orden,
        "cantidad": str(cantidad),
        "precio_limite": str(precio_limite) if precio_limite else "0",
        "precio_disparo": str(precio_disparo_final) if precio_disparo_final else "0",
        "moneda_reservada": moneda_reservada,
        "cantidad_reservada": str(cantidad_reservada),
        "moneda_origen": moneda_reservada,
        "moneda_destino": moneda_principal if accion == config.ACCION_COMPRAR else moneda_cotizada,
        "estado": config.ESTADO_PENDIENTE if tipo_orden in [config.TIPO_ORDEN_LIMITE, config.TIPO_ORDEN_STOP_LIMIT] else config.ESTADO_EJECUTADA,
        "timestamp_creacion": datetime.now().isoformat(),
        "timestamp_ejecucion": None,
        "cantidad_destino_final": "0"
    }
    
    return nueva_orden