# backend/servicios/trading/gestor.py
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes
from backend.utils.responses import crear_respuesta_error, crear_respuesta_exitosa
from backend.utils.utilidades_numericas import a_decimal, formato_cantidad_cripto
from backend.servicios.estado_billetera import estado_actual_completo
from config import (
    ESTADO_ERROR, ESTADO_PENDIENTE, ESTADO_CANCELADA, ESTADO_EJECUTADA,
    TIPO_ORDEN_MERCADO
)

def crear_orden(
    par: str,
    tipo_orden: str,
    accion: str,
    cantidad: Decimal,
    precio_limite: Decimal = None,
    precio_disparo: Decimal = None
) -> Dict[str, Any]:
    """
    Crea una nueva orden, reserva los fondos necesarios y la guarda en el sistema.
    Si la orden es de tipo 'market', se intenta ejecutar inmediatamente.
    """
    # Importación local para evitar dependencia circular
    from backend.servicios.trading.motor import _crear_nueva_orden, _ejecutar_orden_pendiente

    nueva_orden = _crear_nueva_orden(par, tipo_orden, accion, cantidad, precio_limite, precio_disparo)

    if ESTADO_ERROR in nueva_orden:
        return nueva_orden

    billetera = cargar_billetera()
    moneda_a_reservar = nueva_orden["moneda_reservada"]
    cantidad_a_reservar = a_decimal(nueva_orden["cantidad_reservada"])

    # Verificación robusta de fondos disponibles
    if billetera.get(moneda_a_reservar, {}).get('saldos', {}).get('disponible', Decimal('0')) < cantidad_a_reservar:
        return {ESTADO_ERROR: f"Fondos insuficientes de {moneda_a_reservar}."}

    # Reservar fondos
    billetera[moneda_a_reservar]['saldos']['disponible'] -= cantidad_a_reservar
    billetera[moneda_a_reservar]['saldos']['reservado'] += cantidad_a_reservar

    # Las órdenes de mercado se ejecutan inmediatamente
    if nueva_orden["tipo_orden"] == TIPO_ORDEN_MERCADO:
        print(f"📈 Orden de mercado detectada ({nueva_orden['id_orden']}). Ejecutando inmediatamente...")
        billetera = _ejecutar_orden_pendiente(nueva_orden, billetera)

    # Guardar estado
    todas_las_ordenes = cargar_ordenes_pendientes()
    
    # Reemplazar la orden si ya existe (caso de orden de mercado que se actualizó) o añadirla si es nueva
    orden_existente_idx = next((i for i, o in enumerate(todas_las_ordenes) if o.get("id_orden") == nueva_orden['id_orden']), -1)
    if orden_existente_idx != -1:
        todas_las_ordenes[orden_existente_idx] = nueva_orden
    else:
        todas_las_ordenes.append(nueva_orden)
    
    guardar_ordenes_pendientes(todas_las_ordenes)
    guardar_billetera(billetera)

    print(f"✅ Orden {nueva_orden['id_orden']} creada exitosamente.")
    return nueva_orden


def cancelar_orden_pendiente(id_orden: str) -> Dict:
    """
    Busca una orden pendiente por su ID, la cancela y libera los fondos reservados.
    """
    todas_las_ordenes = cargar_ordenes_pendientes()
    orden_a_cancelar = next((o for o in todas_las_ordenes if o.get("id_orden") == id_orden), None)

    if not orden_a_cancelar:
        return crear_respuesta_error(f"No se encontró una orden con el ID {id_orden}.")

    if orden_a_cancelar.get("estado") != ESTADO_PENDIENTE:
        return crear_respuesta_error(f"La orden {id_orden} no está pendiente y no puede ser cancelada.")

    billetera = cargar_billetera()
    moneda_reservada = orden_a_cancelar["moneda_reservada"]
    cantidad_reservada = a_decimal(orden_a_cancelar["cantidad_reservada"])

    activo_en_billetera = billetera.get(moneda_reservada)

    # Verificación de consistencia de fondos
    if not activo_en_billetera or a_decimal(activo_en_billetera.get("saldos", {}).get("reservado", Decimal('0'))) < cantidad_reservada:
        orden_a_cancelar["estado"] = ESTADO_ERROR
        orden_a_cancelar["mensaje_error"] = "Error de consistencia: los fondos a liberar no coinciden con la billetera."
        guardar_ordenes_pendientes(todas_las_ordenes)
        return crear_respuesta_error(orden_a_cancelar["mensaje_error"])

    # Liberar fondos
    activo_en_billetera["saldos"]["reservado"] -= cantidad_reservada
    activo_en_billetera["saldos"]["disponible"] += cantidad_reservada

    # Actualizar estado de la orden
    orden_a_cancelar["estado"] = ESTADO_CANCELADA
    orden_a_cancelar["timestamp_cancelacion"] = datetime.now().isoformat()

    guardar_ordenes_pendientes(todas_las_ordenes)
    guardar_billetera(billetera)

    # Devolver una respuesta clara y útil para el frontend
    mensaje_exito = f"Orden {orden_a_cancelar['par']} cancelada. Se liberaron {formato_cantidad_cripto(cantidad_reservada)} {moneda_reservada}."
    
    billetera_actualizada_completa = estado_actual_completo()
    activo_modificado = next((a for a in billetera_actualizada_completa if a['ticker'] == moneda_reservada), None)

    datos_exito = {
        "orden_cancelada": orden_a_cancelar,
        "activo_actualizado": activo_modificado
    }
    return crear_respuesta_exitosa(datos_exito, mensaje_exito)