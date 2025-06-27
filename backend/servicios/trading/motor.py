# backend/servicios/trading/motor.py

from datetime import datetime
from decimal import Decimal

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes
from backend.servicios.trading.ejecutar_orden import ejecutar_transaccion
from backend.utils.utilidades_numericas import a_decimal, cuantizar_cripto

def _verificar_condicion_orden(orden: dict, precio_actual: Decimal) -> bool:
    """Verifica si el precio actual cumple la condición de DISPARO (Stop) de la orden."""
    precio_disparo = a_decimal(orden["precio_disparo"])
    tipo_orden = orden.get("tipo_orden", "limit") # Por defecto, 'limit' si no está definido
    
    # Para órdenes Límite
    if tipo_orden == "limit":
        if orden["accion"] == "compra":
            return precio_actual <= precio_disparo
        elif orden["accion"] == "venta":
            return precio_actual >= precio_disparo
            
    # Para órdenes Stop-Limit (antes 'stop-loss')
    elif tipo_orden == "stop-limit":
        # Para una compra stop, queremos comprar cuando el precio SUBE a un nivel.
        if orden["accion"] == "compra":
            return precio_actual >= precio_disparo
        # Para una venta stop, queremos vender cuando el precio CAE a un nivel.
        elif orden["accion"] == "venta":
            return precio_actual <= precio_disparo

    return False

def _ejecutar_orden_pendiente(orden: dict, billetera: dict) -> dict:
    """
    Ejecuta una orden pendiente que ya ha sido disparada,
    con lógica especial para la verificación del precio límite en órdenes Stop-Limit.
    """
    # ### NUEVO: VERIFICACIÓN DEL PRECIO LÍMITE PARA ÓRDENES STOP-LIMIT ###
    if orden.get("tipo_orden") == "stop-limit":
        precio_limite = a_decimal(orden.get("precio_limite"))
        
        # Si no hay precio límite en la orden, es un error de datos.
        if not precio_limite or precio_limite.is_zero():
             print(f"❌ ERROR DE DATOS: Orden Stop-Limit {orden['id_orden']} no tiene precio límite válido.")
             orden["estado"] = "error_datos"
             return billetera
             
        # Obtenemos el precio de mercado actual para la comprobación del límite.
        ticker_base = orden["par"].split('/')[0]
        precio_actual_mercado = obtener_precio(ticker_base)

        if not precio_actual_mercado:
             print(f"⚠️ No se pudo obtener precio para la verificación límite de la orden {orden['id_orden']}. Se reintentará.")
             return billetera # No hacemos nada, esperamos al siguiente ciclo

        # Condición de ejecución para COMPRA LÍMITE (después del stop)
        if orden["accion"] == "compra" and precio_actual_mercado > precio_limite:
            print(f"🚦 ORDEN STOP-LIMIT {orden['id_orden']} DISPARADA, PERO NO EJECUTADA: Precio actual ({precio_actual_mercado}) > Precio Límite ({precio_limite}).")
            return billetera # Se mantiene pendiente hasta que el precio sea favorable
        
        # Condición de ejecución para VENTA LÍMITE (después del stop)
        elif orden["accion"] == "venta" and precio_actual_mercado < precio_limite:
            print(f"🚦 ORDEN STOP-LIMIT {orden['id_orden']} DISPARADA, PERO NO EJECUTADA: Precio actual ({precio_actual_mercado}) < Precio Límite ({precio_limite}).")
            return billetera # Se mantiene pendiente hasta que el precio sea favorable

    # --- Lógica de ejecución de la transacción (común a Limit y Stop-Limit que pasaron el filtro) ---
    moneda_origen = orden["moneda_reservada"]
    cantidad_origen_bruta = a_decimal(orden["cantidad_reservada"])
    # Para una compra, el destino es la cripto principal. Para una venta, el origen es la cripto principal.
    moneda_destino = orden["moneda_destino"] if orden["accion"] == "compra" else orden["moneda_origen"]

    # Aquí es importante determinar correctamente el destino final de la transacción
    # Si es una compra, la moneda destino es la moneda principal del par.
    # Si es una venta, la moneda destino es la moneda cotizada (quote).
    moneda_destino_final = orden["moneda_destino"]

    tipo_op_historial = f"{orden['tipo_orden'].replace('-', ' ').title()} {orden['accion'].title()}"
    
    exito_ejecucion, detalles_ejecucion = ejecutar_transaccion(
        billetera=billetera,
        moneda_origen=moneda_origen,
        cantidad_origen_bruta=cantidad_origen_bruta,
        moneda_destino=moneda_destino_final,
        tipo_operacion_historial=tipo_op_historial,
        es_orden_pendiente=True
    )
    
    if not exito_ejecucion:
        print(f"❌ ERROR al ejecutar orden pendiente {orden['id_orden']}: {detalles_ejecucion.get('error')}")
        orden.update({"estado": "error_ejecucion", "mensaje_error": detalles_ejecucion.get("error")})
        return billetera

    print(f"✅ ORDEN EJECUTADA: {orden['id_orden']} ({orden['par']})")
    orden.update({
        "estado": "ejecutada",
        "timestamp_ejecucion": datetime.now().isoformat(),
        "cantidad_destino_final": str(cuantizar_cripto(detalles_ejecucion["cantidad_destino_final"]))
    })
    
    return billetera

def verificar_y_ejecutar_ordenes_pendientes():
    """Motor principal que itera sobre órdenes pendientes y las ejecuta si cumplen la condición."""
    todas_las_ordenes = cargar_ordenes_pendientes()
    ordenes_activas = [o for o in todas_las_ordenes if o.get("estado") == "pendiente"]
    if not ordenes_activas: 
        return

    billetera = cargar_billetera()
    precios_cacheados = {}
    alguna_orden_ejecutada = False

    for orden in ordenes_activas:
        ticker_principal = orden["par"].split('/')[0]
        if ticker_principal not in precios_cacheados:
            precios_cacheados[ticker_principal] = obtener_precio(ticker_principal)
        
        precio_actual = precios_cacheados[ticker_principal]
        if precio_actual and _verificar_condicion_orden(orden, precio_actual):
            billetera = _ejecutar_orden_pendiente(orden, billetera)
            # Verificamos si la orden cambió de estado
            if orden.get("estado") != "pendiente":
                alguna_orden_ejecutada = True

    if alguna_orden_ejecutada:
        print("💾 Guardando cambios en billetera y lista de órdenes...")
        guardar_billetera(billetera)
        guardar_ordenes_pendientes(todas_las_ordenes)