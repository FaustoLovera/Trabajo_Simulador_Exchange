"""Módulo Fachada para la Gestión del Ciclo de Vida de Órdenes.

Este módulo proporciona la API pública de alto nivel para interactuar con el
subsistema de trading. Actúa como una fachada que simplifica la creación y
cancelación de órdenes, orquestando las interacciones entre la billetera,
el libro de órdenes y el motor de ejecución.

A diferencia de `procesador.py`, que maneja datos de formularios, este módulo
ofrece una interfaz más abstracta y programática.
"""
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime

import config
from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes
from backend.servicios.estado_billetera import estado_actual_completo
from backend.servicios.trading.motor import _crear_nueva_orden, _ejecutar_orden_pendiente
from backend.utils.responses import crear_respuesta_error, crear_respuesta_exitosa
from backend.utils.utilidades_numericas import a_decimal, formato_cantidad_cripto

# --- Funciones Auxiliares Privadas ---

def _validar_fondos_disponibles(billetera: Dict[str, Any], moneda: str, cantidad_requerida: Decimal) -> bool:
    """
    Verifica de forma segura y legible si hay suficientes fondos disponibles en la billetera.
    """
    activo = billetera.get(moneda, {})
    saldos = activo.get("saldos", {})
    saldo_disponible = a_decimal(saldos.get("disponible", "0"))
    return saldo_disponible >= cantidad_requerida

def _validar_fondos_reservados(billetera: Dict[str, Any], moneda: str, cantidad_a_liberar: Decimal) -> bool:
    """
    Verifica de forma segura y legible si los fondos reservados son consistentes.
    """
    activo = billetera.get(moneda, {})
    saldos = activo.get("saldos", {})
    saldo_reservado = a_decimal(saldos.get("reservado", "0"))
    return saldo_reservado >= cantidad_a_liberar

# --- Funciones Públicas del Módulo ---

def crear_orden(
    par: str,
    tipo_orden: str,
    accion: str,
    cantidad: Decimal,
    precio_limite: Decimal | None = None,
    precio_disparo: Decimal | None = None,
) -> Dict[str, Any]:
    """Orquesta la creación y posible ejecución inmediata de una orden."""
    # 1. Crear la estructura de la orden usando la fábrica centralizada.
    nueva_orden = _crear_nueva_orden(par, tipo_orden, accion, cantidad, precio_limite, precio_disparo)
    if config.ESTADO_ERROR in nueva_orden:
        return nueva_orden

    # 2. Cargar billetera y validar fondos.
    billetera = cargar_billetera()
    moneda_a_reservar = nueva_orden["moneda_reservada"]
    cantidad_a_reservar = a_decimal(nueva_orden["cantidad_reservada"])

    if not _validar_fondos_disponibles(billetera, moneda_a_reservar, cantidad_a_reservar):
        return crear_respuesta_error(f"Fondos insuficientes de {moneda_a_reservar}.")

    # 3. Reservar fondos (operación en memoria).
    billetera[moneda_a_reservar]['saldos']['disponible'] -= cantidad_a_reservar
    billetera[moneda_a_reservar]['saldos']['reservado'] += cantidad_a_reservar

    # 4. Si es una orden de mercado, ejecutarla inmediatamente.
    if nueva_orden["tipo_orden"] == config.TIPO_ORDEN_MERCADO:
        print(f"📈 Orden de mercado detectada ({nueva_orden['id_orden']}). Ejecutando inmediatamente...")
        billetera = _ejecutar_orden_pendiente(nueva_orden, billetera)

    # 5. Persistir los cambios en los archivos de datos.
    todas_las_ordenes = cargar_ordenes_pendientes()
    
    # Busca si la orden ya existe para reemplazarla (caso de una orden de mercado
    # que se ejecutó y su estado cambió), si no, la añade.
    indices_existentes = [i for i, o in enumerate(todas_las_ordenes) if o.get("id_orden") == nueva_orden['id_orden']]
    if indices_existentes:
        todas_las_ordenes[indices_existentes[0]] = nueva_orden
    else:
        todas_las_ordenes.append(nueva_orden)
    
    guardar_ordenes_pendientes(todas_las_ordenes)
    guardar_billetera(billetera)

    print(f"✅ Orden {nueva_orden['id_orden']} creada exitosamente.")
    return nueva_orden

def cancelar_orden_pendiente(id_orden: str) -> Dict[str, Any]:
    """Cancela una orden pendiente y libera los fondos asociados."""
    todas_las_ordenes = cargar_ordenes_pendientes()
    
    # Filtrar la orden por ID usando comprensión de listas
    ordenes_encontradas = [o for o in todas_las_ordenes if o.get("id_orden") == id_orden]
    orden_a_cancelar = ordenes_encontradas[0] if ordenes_encontradas else None

    if not orden_a_cancelar:
        return crear_respuesta_error(f"No se encontró una orden con el ID {id_orden}.")

    if orden_a_cancelar.get("estado") != config.ESTADO_PENDIENTE:
        estado_actual = orden_a_cancelar.get("estado", "desconocido")
        return crear_respuesta_error(f"La orden {id_orden} no puede ser cancelada (estado actual: '{estado_actual}').")

    billetera = cargar_billetera()
    moneda_reservada = orden_a_cancelar["moneda_reservada"]
    cantidad_a_liberar = a_decimal(orden_a_cancelar["cantidad_reservada"])
    
    # Verificación de consistencia de fondos reservados
    if not _validar_fondos_reservados(billetera, moneda_reservada, cantidad_a_liberar):
        orden_a_cancelar["estado"] = config.ESTADO_ERROR
        orden_a_cancelar["mensaje_error"] = "Error de consistencia: los fondos a liberar no coinciden con la billetera."
        guardar_ordenes_pendientes(todas_las_ordenes)
        return crear_respuesta_error(orden_a_cancelar["mensaje_error"])

    # Liberar fondos (operación en memoria)
    activo_en_billetera = billetera[moneda_reservada]
    activo_en_billetera["saldos"]["reservado"] -= cantidad_a_liberar
    activo_en_billetera["saldos"]["disponible"] += cantidad_a_liberar

    # Actualizar estado de la orden
    orden_a_cancelar["estado"] = config.ESTADO_CANCELADA
    orden_a_cancelar["timestamp_cancelacion"] = datetime.now().isoformat()

    # Persistir todos los cambios
    guardar_ordenes_pendientes(todas_las_ordenes)
    guardar_billetera(billetera)

    # Construir y devolver una respuesta clara para el frontend
    mensaje_exito = f"Orden {orden_a_cancelar['par']} cancelada. Se liberaron {formato_cantidad_cripto(cantidad_a_liberar)} {moneda_reservada}."
    
    # Obtener el estado actualizado del activo para refrescar la UI
    billetera_actualizada_completa = estado_actual_completo()

    # Encontrar el activo modificado en la billetera actualizada
    activos_encontrados = [a for a in billetera_actualizada_completa if a['ticker'] == moneda_reservada]
    activo_modificado = activos_encontrados[0] if activos_encontrados else None

    datos_exito = {
        "orden_cancelada": orden_a_cancelar,
        "activo_actualizado": activo_modificado
    }
    return crear_respuesta_exitosa(datos_exito, mensaje_exito)