# backend/servicios/trading/motor.py

from datetime import datetime
from decimal import Decimal

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio, cargar_datos_cotizaciones
from backend.acceso_datos.datos_historial import guardar_en_historial
from backend.acceso_datos.datos_comisiones import registrar_comision
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes
from backend.utils.utilidades_numericas import a_decimal, cuantizar_cripto
from config import TASA_COMISION

# --- Funciones Auxiliares (privadas a este módulo) ---

def _crear_activo_si_no_existe(billetera: dict, ticker: str):
    if ticker not in billetera:
        info_criptos = {c['ticker']: c for c in cargar_datos_cotizaciones()}
        info_nueva_moneda = info_criptos.get(ticker, {"nombre": ticker})
        billetera[ticker] = {"nombre": info_nueva_moneda.get("nombre", ticker), "saldos": {"disponible": a_decimal("0"), "reservado": a_decimal("0")}}

def _verificar_condicion_orden(orden: dict, precio_actual: Decimal) -> bool:
    precio_disparo = a_decimal(orden["precio_disparo"])
    if orden["accion"] == "compra":
        return precio_actual <= precio_disparo if orden["tipo_orden"] == "limit" else precio_actual >= precio_disparo
    elif orden["accion"] == "venta":
        return precio_actual >= precio_disparo if orden["tipo_orden"] == "limit" else precio_actual <= precio_disparo
    return False

def _ejecutar_orden_pendiente(orden: dict, billetera: dict) -> dict:
    moneda_origen, moneda_destino = orden["moneda_origen"], orden["moneda_destino"]
    cantidad_origen_reservada = a_decimal(orden["cantidad_origen"])

    billetera[moneda_origen]["saldos"]["reservado"] -= cantidad_origen_reservada

    precio_origen_usdt = obtener_precio(moneda_origen)
    precio_destino_usdt = obtener_precio(moneda_destino)
    if not all([precio_origen_usdt, precio_destino_usdt]): return billetera

    cantidad_comision = cantidad_origen_reservada * TASA_COMISION
    registrar_comision(moneda_origen, cantidad_comision, cantidad_comision * precio_origen_usdt)

    cantidad_origen_neta = cantidad_origen_reservada - cantidad_comision
    valor_neto_usd = cantidad_origen_neta * precio_origen_usdt
    cantidad_destino_neta_final = valor_neto_usd / precio_destino_usdt

    _crear_activo_si_no_existe(billetera, moneda_destino)
    billetera[moneda_destino]["saldos"]["disponible"] += cantidad_destino_neta_final

    guardar_en_historial(f"{orden['tipo_orden']}-{orden['accion']}", moneda_origen, cantidad_origen_neta, moneda_destino, cantidad_destino_neta_final, valor_neto_usd)
    
    print(f"✅ ORDEN EJECUTADA: {orden['id_orden']} ({orden['par']})")
    orden.update({"estado": "ejecutada", "timestamp_ejecucion": datetime.now().isoformat(), "cantidad_destino_final": str(cuantizar_cripto(cantidad_destino_neta_final))})
    return billetera

# --- Punto de Entrada Público ---

def verificar_y_ejecutar_ordenes_pendientes():
    """Motor principal que itera sobre órdenes pendientes y las ejecuta si cumplen la condición."""
    todas_las_ordenes = cargar_ordenes_pendientes()
    ordenes_activas = [o for o in todas_las_ordenes if o.get("estado") == "pendiente"]
    if not ordenes_activas: return

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