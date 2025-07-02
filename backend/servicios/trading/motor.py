# backend/servicios/trading/motor.py
from datetime import datetime
from decimal import Decimal

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes
from config import (
    ACCION_COMPRAR,
    ACCION_VENDER,
    ESTADO_EJECUTADA,
    ESTADO_PENDIENTE,
    ESTADO_ERROR,
    TIPO_ORDEN_LIMITE,
    TIPO_ORDEN_MERCADO,
    TIPO_ORDEN_STOP_LIMIT
)
from backend.servicios.trading.ejecutar_orden import ejecutar_transaccion
from backend.utils.utilidades_numericas import a_decimal, cuantizar_cripto


def _verificar_condicion_orden(orden: dict, precio_actual: Decimal) -> bool:
    """Verifica si el precio actual cumple la condición de DISPARO de la orden."""
    precio_disparo = a_decimal(orden["precio_disparo"])
    tipo_orden = orden.get("tipo_orden", TIPO_ORDEN_LIMITE)

    if tipo_orden == TIPO_ORDEN_LIMITE:
        if orden["accion"] == ACCION_COMPRAR:
            return precio_actual <= precio_disparo
        elif orden["accion"] == ACCION_VENDER:
            return precio_actual >= precio_disparo
            
    elif tipo_orden == TIPO_ORDEN_STOP_LIMIT:
        if orden["accion"] == ACCION_COMPRAR:
            return precio_actual >= precio_disparo
        elif orden["accion"] == ACCION_VENDER:
            return precio_actual <= precio_disparo

    return False


def _ejecutar_orden_pendiente(orden: dict, billetera: dict) -> dict:
    """
    Intenta ejecutar una orden que ya ha sido disparada (condición cumplida),
    con lógica especial para la verificación del precio límite en órdenes Stop-Limit.
    """
    if orden.get("tipo_orden") == TIPO_ORDEN_STOP_LIMIT:
        precio_limite = a_decimal(orden.get("precio_limite"))
        
        if not precio_limite or precio_limite.is_zero():
             print(f"❌ ERROR DE DATOS: Orden Stop-Limit {orden['id_orden']} no tiene precio límite válido.")
             orden["estado"] = ESTADO_ERROR
             return billetera
              
        precio_actual_mercado = obtener_precio(orden["par"])
        if not precio_actual_mercado:
             print(f"⚠️  No se pudo obtener el precio de mercado para {orden['par']} para validar el límite de la orden {orden['id_orden']}.")
             return billetera

        if orden["accion"] == ACCION_COMPRAR and precio_actual_mercado > precio_limite:
            print(f"🚦 ORDEN STOP-LIMIT {orden['id_orden']} DISPARADA, PERO NO EJECUTADA: Precio actual ({precio_actual_mercado}) > Precio Límite ({precio_limite}).")
            return billetera
        
        elif orden["accion"] == ACCION_VENDER and precio_actual_mercado < precio_limite:
            print(f"🚦 ORDEN STOP-LIMIT {orden['id_orden']} DISPARADA, PERO NO EJECUTADA: Precio actual ({precio_actual_mercado}) < Precio Límite ({precio_limite}).")
            return billetera

    moneda_origen = orden["moneda_reservada"]
    cantidad_origen_bruta = a_decimal(orden["cantidad_reservada"])
    # Corregido: La moneda de destino se saca del par, no de la propia orden directamente.
    moneda_destino = orden["par"].split('/')[0] if orden["accion"] == ACCION_COMPRAR else orden["par"].split('/')[1]
    
    # El tipo de operación para el historial debe ser más descriptivo
    tipo_op_historial = f"{orden['tipo_orden']}-{orden['accion']}"

    # --- LLAMADA CORREGIDA ---
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
        orden.update({"estado": ESTADO_ERROR, "mensaje_error": detalles_ejecucion.get("error")})
        return billetera

    print(f"✅ ORDEN EJECUTADA: {orden['id_orden']} ({orden['par']})")
    orden.update({
        "estado": ESTADO_EJECUTADA,
        "timestamp_ejecucion": datetime.now().isoformat(),
        "cantidad_destino_final": str(cuantizar_cripto(detalles_ejecucion["cantidad_destino_final"]))
    })
    return billetera


def verificar_y_ejecutar_ordenes_pendientes():
    """Motor principal que itera sobre órdenes pendientes y las ejecuta si cumplen la condición."""
    todas_las_ordenes = cargar_ordenes_pendientes()
    ordenes_pendientes = [o for o in todas_las_ordenes if o.get("estado") == ESTADO_PENDIENTE]
    if not ordenes_pendientes: 
        return

    billetera = cargar_billetera()
    ordenes_modificadas = []
    
    for orden in ordenes_pendientes:
        precio_actual = obtener_precio(orden["par"])
        if not precio_actual:
            print(f"⚠️  No se pudo obtener precio para el par {orden['par']}. Saltando orden {orden['id_orden']}.")
            continue

        if _verificar_condicion_orden(orden, precio_actual):
            print(f"🔔 CONDICIÓN CUMPLIDA para orden {orden['id_orden']}. Intentando ejecutar...")
            billetera = _ejecutar_orden_pendiente(orden, billetera)
        
        ordenes_modificadas.append(orden)

    ordenes_no_modificadas = [o for o in todas_las_ordenes if o.get("estado") != ESTADO_PENDIENTE]
    
    guardar_ordenes_pendientes(ordenes_no_modificadas + ordenes_modificadas)
    guardar_billetera(billetera)
    print("--- Ciclo de motor de trading finalizado ---")


def _crear_nueva_orden(par, tipo_orden, accion, cantidad, precio_limite=None, precio_disparo=None):
    """
    Valida los datos de una nueva orden y la estructura para ser guardada.
    No guarda la orden, solo la prepara y valida.
    """
    if tipo_orden not in [TIPO_ORDEN_MERCADO, TIPO_ORDEN_LIMITE, TIPO_ORDEN_STOP_LIMIT]:
        return {ESTADO_ERROR: "Tipo de orden no válido"}
    
    if accion not in [ACCION_COMPRAR, ACCION_VENDER]:
        return {ESTADO_ERROR: "Acción no válida"}

    if tipo_orden in [TIPO_ORDEN_LIMITE, TIPO_ORDEN_STOP_LIMIT] and (not precio_limite or precio_limite <= 0):
        return {ESTADO_ERROR: "El precio límite es obligatorio para órdenes límite y stop-limit"}

    if tipo_orden == TIPO_ORDEN_STOP_LIMIT and (not precio_disparo or precio_disparo <= 0):
        return {ESTADO_ERROR: "El precio de disparo es obligatorio para órdenes stop-limit"}

    moneda_principal, moneda_cotizada = par.split('/')
    
    if accion == ACCION_COMPRAR:
        moneda_reservada = moneda_cotizada
        cantidad_reservada = cantidad if tipo_orden == TIPO_ORDEN_MERCADO else cantidad * precio_limite
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
        "moneda_destino": moneda_principal if accion == ACCION_COMPRAR else moneda_cotizada,
        "estado": ESTADO_PENDIENTE if tipo_orden in [TIPO_ORDEN_LIMITE, TIPO_ORDEN_STOP_LIMIT] else ESTADO_EJECUTADA,
        "timestamp_creacion": datetime.now().isoformat(),
        "timestamp_ejecucion": None,
        "cantidad_destino_final": "0"
    }
    
    return nueva_orden