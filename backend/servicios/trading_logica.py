# backend/servicios/trading_logica.py

"""
Servicio para la lógica de negocio de operaciones de trading (swap).

Este módulo contiene toda la lógica para procesar, validar y ejecutar un
intercambio de criptomonedas, incluyendo el cálculo y cobro de comisiones,
y ahora también la creación y ejecución de órdenes pendientes (Límite, Stop-Loss).
"""

import uuid
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Tuple

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.acceso_datos.datos_historial import guardar_en_historial
from backend.acceso_datos.datos_comisiones import registrar_comision
# Importamos las funciones para cargar y guardar las órdenes
from backend.acceso_datos.datos_ordenes import (
    agregar_orden_pendiente,
    cargar_ordenes_pendientes,
    guardar_ordenes_pendientes,
)
from config import TASA_COMISION


# --- Funciones Auxiliares ---

def _validar_saldo_disponible(billetera: dict, moneda_origen: str, cantidad_requerida: Decimal) -> Tuple[bool, str | None]:
    """Verifica si hay suficiente saldo DISPONIBLE en la billetera."""
    saldo_disponible = billetera.get(moneda_origen, {}).get("disponible", Decimal("0"))
    if cantidad_requerida > saldo_disponible:
        mensaje_error = (
            f"❌ Saldo insuficiente. Tienes {saldo_disponible:.8f} {moneda_origen} disponibles, "
            f"pero se requieren {cantidad_requerida:.8f}."
        )
        return False, mensaje_error
    return True, None


# --- Lógica para Órdenes de Mercado (Market) ---

def _ejecutar_orden_mercado(moneda_origen: str, moneda_destino: str, monto_form: Decimal, modo_ingreso: str, accion: str) -> Tuple[bool, str]:
    """Procesa una orden de mercado (ejecución inmediata)."""
    precio_origen_usdt = obtener_precio(moneda_origen)
    precio_destino_usdt = obtener_precio(moneda_destino)

    if precio_origen_usdt is None or precio_destino_usdt is None or precio_origen_usdt.is_zero() or precio_destino_usdt.is_zero():
        return False, "❌ No se pudo obtener la cotización para realizar el swap."

    if accion == 'comprar':
        if modo_ingreso == 'monto':
            cantidad_destino_bruta = monto_form
            valor_total_usd = cantidad_destino_bruta * precio_destino_usdt
            cantidad_origen_bruta = valor_total_usd / precio_origen_usdt
        else: # 'total'
            cantidad_origen_bruta = monto_form
            valor_total_usd = cantidad_origen_bruta * precio_origen_usdt
            cantidad_destino_bruta = valor_total_usd / precio_destino_usdt
    else: # 'vender'
        cantidad_origen_bruta = monto_form
        valor_total_usd = cantidad_origen_bruta * precio_origen_usdt
        cantidad_destino_bruta = valor_total_usd / precio_destino_usdt

    billetera = cargar_billetera()
    exito_validacion, mensaje_error = _validar_saldo_disponible(billetera, moneda_origen, cantidad_origen_bruta)
    if not exito_validacion:
        return False, mensaje_error

    cantidad_comision = cantidad_origen_bruta * TASA_COMISION
    valor_comision_usd = cantidad_comision * precio_origen_usdt
    registrar_comision(moneda_origen, cantidad_comision, valor_comision_usd)

    cantidad_origen_neta_swap = cantidad_origen_bruta - cantidad_comision
    valor_neto_usd = cantidad_origen_neta_swap * precio_origen_usdt
    cantidad_destino_neta = valor_neto_usd / precio_destino_usdt

    billetera[moneda_origen]["disponible"] -= cantidad_origen_bruta
    if moneda_destino not in billetera:
        billetera[moneda_destino] = {"disponible": Decimal("0"), "reservado": Decimal("0")}
    billetera[moneda_destino]["disponible"] += cantidad_destino_neta
    
    if billetera[moneda_origen]["disponible"] <= Decimal("1e-8") and billetera[moneda_origen]["reservado"] == Decimal("0"):
        billetera.pop(moneda_origen, None)

    guardar_billetera(billetera)

    tipo_operacion = "compra" if moneda_origen == "USDT" else "venta" if moneda_destino == "USDT" else "intercambio"
    guardar_en_historial(
        tipo_operacion,
        moneda_origen, cantidad_origen_neta_swap.quantize(Decimal("0.00000001")),
        moneda_destino, cantidad_destino_neta.quantize(Decimal("0.00000001")),
        valor_neto_usd
    )

    mensaje_exito = (
        f"✅ Operación de mercado exitosa: Se intercambiaron {cantidad_origen_neta_swap:.8f} {moneda_origen} "
        f"por {cantidad_destino_neta:.8f} {moneda_destino}. "
        f"Comisión aplicada: {cantidad_comision:.8f} {moneda_origen}."
    )
    return True, mensaje_exito


# --- Lógica para CREAR Órdenes Pendientes ---

def _crear_orden_pendiente(moneda_origen: str, moneda_destino: str, monto_form: Decimal, precio_disparo: Decimal, tipo_orden: str, accion: str) -> Tuple[bool, str]:
    """Valida y crea una orden pendiente, reservando los fondos necesarios."""
    billetera = cargar_billetera()
    cantidad_a_operar = monto_form

    if accion == 'comprar':
        monto_a_reservar = cantidad_a_operar * precio_disparo
        moneda_a_reservar = moneda_origen
        cantidad_origen_orden = monto_a_reservar
        cantidad_destino_orden = cantidad_a_operar
    else: # 'vender'
        monto_a_reservar = cantidad_a_operar
        moneda_a_reservar = moneda_origen
        cantidad_origen_orden = monto_a_reservar
        cantidad_destino_orden = cantidad_a_operar * precio_disparo # Estimado, se recalcula al ejecutar

    exito_validacion, mensaje_error = _validar_saldo_disponible(billetera, moneda_a_reservar, monto_a_reservar)
    if not exito_validacion:
        return False, mensaje_error

    billetera[moneda_a_reservar]["disponible"] -= monto_a_reservar
    billetera[moneda_a_reservar]["reservado"] += monto_a_reservar
    guardar_billetera(billetera)

    nueva_orden = {
        "id_orden": str(uuid.uuid4()),
        "timestamp_creacion": datetime.now().isoformat(),
        "tipo_orden": tipo_orden,
        "accion": accion,
        "par": f"{moneda_destino}/{moneda_origen}",
        "moneda_origen": moneda_origen,
        "moneda_destino": moneda_destino,
        "cantidad_origen": str(cantidad_origen_orden),
        "cantidad_destino": str(cantidad_destino_orden),
        "precio_disparo": str(precio_disparo),
        "estado": "pendiente"
    }
    agregar_orden_pendiente(nueva_orden)
    
    mensaje_exito = (
        f"✅ Orden {tipo_orden.capitalize()} de {accion} creada para {cantidad_a_operar} {moneda_destino if accion == 'comprar' else moneda_origen} "
        f"a un precio de {precio_disparo}."
    )
    return True, mensaje_exito


# --- Función Principal de Despacho ---

def procesar_operacion_trading(formulario: dict) -> Tuple[bool, str]:
    """Valida y despacha la operación al procesador correcto según el tipo de orden."""
    try:
        ticker_principal = formulario["ticker"].upper()
        accion = formulario["accion"]
        monto_form = Decimal(formulario["monto"])
        modo_ingreso = formulario.get("modo-ingreso", "monto")
        tipo_orden = formulario.get("tipo-orden", "market").lower()
    except (KeyError, InvalidOperation, TypeError) as e:
        return False, f"❌ Error en los datos del formulario: {e}"

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

    if tipo_orden == "market":
        if accion == 'vender' and modo_ingreso == 'total':
             return False, "❌ Al vender, debe ingresar la cantidad en modo 'Cantidad (Cripto)'."
        return _ejecutar_orden_mercado(moneda_origen, moneda_destino, monto_form, modo_ingreso, accion)
    
    elif tipo_orden in ["limit", "stop-loss"]:
        try:
            precio_disparo = Decimal(formulario["precio_disparo"])
            if precio_disparo <= 0:
                return False, "❌ El precio de disparo debe ser positivo."
        except (KeyError, InvalidOperation, TypeError):
            return False, "❌ Se requiere un precio de disparo válido para órdenes Límite/Stop-Loss."
        
        return _crear_orden_pendiente(moneda_origen, moneda_destino, monto_form, precio_disparo, tipo_orden, accion)
    
    else:
        return False, f"❌ Tipo de orden desconocido: '{tipo_orden}'."

# ===================================================================
# === MOTOR DE EJECUCIÓN DE ÓRDENES PENDIENTES (LÓGICA DE FASE 3) ===
# ===================================================================

def _verificar_condicion_orden(orden: dict, precio_actual: Decimal) -> bool:
    """Verifica si la condición de precio para una orden pendiente se ha cumplido."""
    precio_disparo = Decimal(orden["precio_disparo"])
    tipo_orden = orden["tipo_orden"]
    accion = orden["accion"]

    if accion == "compra":
        if tipo_orden == "limit": # Comprar por debajo de un precio
            return precio_actual <= precio_disparo
        elif tipo_orden == "stop-loss": # Comprar por encima de un precio (entrar en breakout)
            return precio_actual >= precio_disparo
    elif accion == "venta":
        if tipo_orden == "limit": # Vender por encima de un precio (tomar ganancias)
            return precio_actual >= precio_disparo
        elif tipo_orden == "stop-loss": # Vender por debajo de un precio (limitar pérdidas)
            return precio_actual <= precio_disparo
    return False

def _ejecutar_orden_pendiente(orden_a_ejecutar: dict, billetera: dict) -> dict:
    """Ejecuta una orden pendiente, actualiza la billetera y el estado de la orden."""
    moneda_origen = orden_a_ejecutar["moneda_origen"]
    moneda_destino = orden_a_ejecutar["moneda_destino"]
    
    # Cantidad que se reservó y ahora se va a usar
    cantidad_origen_reservada = Decimal(orden_a_ejecutar["cantidad_origen"])

    # 1. Liberar los fondos reservados de la billetera
    billetera[moneda_origen]["reservado"] -= cantidad_origen_reservada

    # 2. Calcular comisión y cantidades netas
    precio_origen_usdt = obtener_precio(moneda_origen)
    if not precio_origen_usdt: return billetera # Seguridad

    cantidad_comision = cantidad_origen_reservada * TASA_COMISION
    valor_comision_usd = cantidad_comision * precio_origen_usdt
    registrar_comision(moneda_origen, cantidad_comision, valor_comision_usd)

    cantidad_origen_neta = cantidad_origen_reservada - cantidad_comision
    valor_neto_usd = cantidad_origen_neta * precio_origen_usdt
    
    precio_destino_usdt = obtener_precio(moneda_destino)
    if not precio_destino_usdt: return billetera # Seguridad
    
    cantidad_destino_neta_final = valor_neto_usd / precio_destino_usdt

    # 3. Acreditar los fondos netos en la moneda de destino
    if moneda_destino not in billetera:
        billetera[moneda_destino] = {"disponible": Decimal("0"), "reservado": Decimal("0")}
    billetera[moneda_destino]["disponible"] += cantidad_destino_neta_final

    # 4. Registrar en el historial
    tipo_operacion_historial = f"{orden_a_ejecutar['tipo_orden']}-{orden_a_ejecutar['accion']}"
    guardar_en_historial(
        tipo_operacion_historial,
        moneda_origen, cantidad_origen_neta,
        moneda_destino, cantidad_destino_neta_final,
        valor_neto_usd
    )
    
    print(f"✅ ORDEN EJECUTADA: {orden_a_ejecutar['id_orden']} ({orden_a_ejecutar['par']})")
    
    # 5. Marcar la orden como ejecutada
    orden_a_ejecutar["estado"] = "ejecutada"
    orden_a_ejecutar["timestamp_ejecucion"] = datetime.now().isoformat()
    orden_a_ejecutar["cantidad_destino_final"] = str(cantidad_destino_neta_final) # Guardamos la cantidad real

    return billetera

def verificar_y_ejecutar_ordenes_pendientes():
    """Motor principal. Carga órdenes y precios, y ejecuta las que cumplen condición."""
    print("⚙️  Ejecutando motor de verificación de órdenes pendientes...")
    todas_las_ordenes = cargar_ordenes_pendientes()
    ordenes_activas = [o for o in todas_las_ordenes if o.get("estado") == "pendiente"]
    
    if not ordenes_activas:
        print("⚙️  No hay órdenes pendientes para verificar.")
        return

    billetera = cargar_billetera()
    alguna_orden_ejecutada = False

    for orden in ordenes_activas:
        ticker_principal = orden["par"].split('/')[0]
        precio_actual = obtener_precio(ticker_principal)
        if precio_actual is None:
            continue

        if _verificar_condicion_orden(orden, precio_actual):
            billetera = _ejecutar_orden_pendiente(orden, billetera)
            alguna_orden_ejecutada = True

    if alguna_orden_ejecutada:
        print("💾 Guardando cambios en billetera y lista de órdenes...")
        guardar_billetera(billetera)
        guardar_ordenes_pendientes(todas_las_ordenes) # Guarda la lista completa con los estados actualizados
    else:
        print("⚙️  Verificación completa. Ninguna orden cumplió su condición.")
        

def cancelar_orden_pendiente(id_orden_a_cancelar: str) -> Tuple[bool, str]:
    """
    Busca una orden pendiente por su ID, la cancela, y libera los fondos reservados.
    
    Args:
        id_orden_a_cancelar (str): El ID único de la orden a cancelar.
        
    Returns:
        Tuple[bool, str]: Una tupla con el estado de éxito y un mensaje.
    """
    todas_las_ordenes = cargar_ordenes_pendientes()
    orden_encontrada = None
    
    for orden in todas_las_ordenes:
        if orden.get("id_orden") == id_orden_a_cancelar:
            orden_encontrada = orden
            break
            
    if not orden_encontrada:
        return False, f"❌ No se encontró una orden con el ID {id_orden_a_cancelar}."
        
    if orden_encontrada.get("estado") != "pendiente":
        return False, f"❌ La orden {id_orden_a_cancelar} ya no está pendiente (estado: {orden_encontrada.get('estado')}). No se puede cancelar."

    # --- La orden es válida para cancelación, procedemos ---
    print(f"🔄 Cancelando orden {id_orden_a_cancelar}...")
    
    billetera = cargar_billetera()
    moneda_origen = orden_encontrada["moneda_origen"]
    cantidad_reservada = Decimal(orden_encontrada["cantidad_origen"])

    # 1. Verificar que los fondos reservados existan para evitar inconsistencias
    if billetera.get(moneda_origen, {}).get("reservado", Decimal("0")) < cantidad_reservada:
        # Esto no debería pasar en un sistema normal, pero es una buena salvaguarda.
        orden_encontrada["estado"] = "error_cancelacion"
        guardar_ordenes_pendientes(todas_las_ordenes)
        return False, "❌ Error de consistencia: Los fondos reservados para esta orden no existen en la billetera."

    # 2. Liberar los fondos: mover de 'reservado' a 'disponible'
    billetera[moneda_origen]["reservado"] -= cantidad_reservada
    billetera[moneda_origen]["disponible"] += cantidad_reservada
    
    # 3. Actualizar el estado de la orden
    orden_encontrada["estado"] = "cancelada"
    orden_encontrada["timestamp_cancelacion"] = datetime.now().isoformat()
    
    # 4. Guardar los cambios
    guardar_billetera(billetera)
    guardar_ordenes_pendientes(todas_las_ordenes)
    
    print(f"✅ Orden {id_orden_a_cancelar} cancelada exitosamente.")
    return True, f"✅ Orden {orden_encontrada['par']} cancelada correctamente."