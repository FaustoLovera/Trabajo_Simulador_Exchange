# backend/servicios/trading/motor.py

from datetime import datetime
from decimal import Decimal

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes
from backend.servicios.trading.ejecutar_orden import ejecutar_transaccion
from backend.utils.utilidades_numericas import a_decimal, cuantizar_cripto

# ### INICIO DE LA REFACTORIZACIÓN DE FASE 4 ###

def _verificar_condicion_orden(orden: dict, precio_actual: Decimal) -> bool:
    """(SIN CAMBIOS) Verifica si el precio actual cumple la condición de disparo de la orden."""
    precio_disparo = a_decimal(orden["precio_disparo"])
    if orden["accion"] == "compra":
        return precio_actual <= precio_disparo if orden["tipo_orden"] == "limit" else precio_actual >= precio_disparo
    elif orden["accion"] == "venta":
        return precio_actual >= precio_disparo if orden["tipo_orden"] == "limit" else precio_actual <= precio_disparo
    return False

def _ejecutar_orden_pendiente(orden: dict, billetera: dict) -> dict:
    """
    ### REFACTORIZADO ### - La lógica es ahora mucho más simple y directa.
    """
    # Gracias a la nueva estructura de orden, los datos necesarios son explícitos.
    moneda_origen = orden["moneda_reservada"]
    cantidad_origen_bruta = a_decimal(orden["cantidad_reservada"])
    moneda_destino = orden["moneda_destino"] if orden["accion"] == "compra" else orden["moneda_origen"]
    
    tipo_op_historial = f"{orden['tipo_orden']}-{orden['accion']}"
    
    exito_ejecucion, detalles_ejecucion = ejecutar_transaccion(
        billetera=billetera,
        moneda_origen=moneda_origen,
        cantidad_origen_bruta=cantidad_origen_bruta,
        moneda_destino=moneda_destino,
        tipo_operacion_historial=tipo_op_historial,
        es_orden_pendiente=True # Usa saldo 'reservado'
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

# --- Punto de Entrada Público del Módulo ---

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
            alguna_orden_ejecutada = True

    if alguna_orden_ejecutada:
        print("💾 Guardando cambios en billetera y lista de órdenes...")
        guardar_billetera(billetera)
        guardar_ordenes_pendientes(todas_las_ordenes)

# ### FIN DE LA REFACTORIZACIÓN DE FASE 4 ###