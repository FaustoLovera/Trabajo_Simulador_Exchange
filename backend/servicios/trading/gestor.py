"""Módulo Fachada para la Gestión del Ciclo de Vida de Órdenes.

Este módulo proporciona la API pública de alto nivel para interactuar con el
subsistema de trading. Actúa como una fachada que simplifica la creación y
cancelación de órdenes, orquestando las interacciones entre la billetera,
el libro de órdenes y el motor de ejecución.

A diferencia de `procesador.py`, que maneja datos de formularios, este módulo
ofrece una interfaz más abstracta y programática.

Responsabilidades Clave:
-   `crear_orden`: Orquesta la validación, reserva de fondos y persistencia de
    una nueva orden. Ejecuta inmediatamente las órdenes de mercado.
-   `cancelar_orden_pendiente`: Gestiona la cancelación de una orden, liberando
    los fondos reservados y actualizando su estado.
"""
from typing import Dict, Any
from decimal import Decimal
from datetime import datetime

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes, guardar_ordenes_pendientes
from backend.utils.responses import crear_respuesta_error, crear_respuesta_exitosa
from backend.utils.utilidades_numericas import a_decimal, formato_cantidad_cripto
from backend.servicios.estado_billetera import estado_actual_completo
import config

def crear_orden(
    par: str,
    tipo_orden: str,
    accion: str,
    cantidad: Decimal,
    precio_limite: Decimal | None = None,
    precio_disparo: Decimal | None = None,
) -> Dict[str, Any]:
    """Orquesta la creación y posible ejecución inmediata de una orden.

    Esta función es la puerta de entrada para crear cualquier tipo de orden.
    Su pipeline es el siguiente:
    1.  Delega la creación del objeto `orden` al `motor`.
    2.  Carga la billetera y valida que haya fondos suficientes.
    3.  Reserva los fondos necesarios (mueve de 'disponible' a 'reservado').
    4.  Si es una orden de mercado, la ejecuta inmediatamente.
    5.  Persiste la orden (nueva o actualizada) y la billetera.

    Args:
        par: El par de trading (ej. "BTC/USDT").
        tipo_orden: 'market', 'limit', 'stop_loss', etc.
        accion: 'compra' o 'venta'.
        cantidad: La cantidad de la moneda base a operar.
        precio_limite: El precio para órdenes 'limit'.
        precio_disparo: El precio para órdenes 'stop'.

    Returns:
        Un diccionario que representa la orden creada o un mensaje de error.
    """
    # Importación local para romper una dependencia circular entre `gestor` y `motor`.
    # `gestor` orquesta y llama a `motor`, pero `motor` podría necesitar
    # en el futuro funcionalidades de `gestor`.
    from backend.servicios.trading.motor import _crear_nueva_orden, _ejecutar_orden_pendiente

    nueva_orden = _crear_nueva_orden(par, tipo_orden, accion, cantidad, precio_limite, precio_disparo)

    if config.ESTADO_ERROR in nueva_orden:
        return nueva_orden

    billetera = cargar_billetera()
    moneda_a_reservar = nueva_orden["moneda_reservada"]
    cantidad_a_reservar = a_decimal(nueva_orden["cantidad_reservada"])

    # Verificación robusta de fondos disponibles
    if billetera.get(moneda_a_reservar, {}).get('saldos', {}).get('disponible', Decimal('0')) < cantidad_a_reservar:
        return {config.ESTADO_ERROR: f"Fondos insuficientes de {moneda_a_reservar}."}

    # Reservar fondos
    billetera[moneda_a_reservar]['saldos']['disponible'] -= cantidad_a_reservar
    billetera[moneda_a_reservar]['saldos']['reservado'] += cantidad_a_reservar

    # Las órdenes de mercado se ejecutan inmediatamente
    if nueva_orden["tipo_orden"] == config.TIPO_ORDEN_MERCADO:
        print(f"📈 Orden de mercado detectada ({nueva_orden['id_orden']}). Ejecutando inmediatamente...")
        billetera = _ejecutar_orden_pendiente(nueva_orden, billetera)

        # Persistir los cambios en la billetera y la lista de órdenes
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


def cancelar_orden_pendiente(id_orden: str) -> Dict[str, Any]:
    """Cancela una orden pendiente y libera los fondos asociados.

    Pipeline de cancelación:
    1.  Busca la orden por su ID en la lista de órdenes pendientes.
    2.  Valida que la orden exista y esté en estado 'pendiente'.
    3.  Carga la billetera y realiza una comprobación de consistencia de fondos.
    4.  Libera los fondos (mueve de 'reservado' a 'disponible').
    5.  Actualiza el estado de la orden a 'cancelada'.
    6.  Persiste la lista de órdenes y la billetera.
    7.  Devuelve una respuesta detallada para el frontend.

    Args:
        id_orden: El identificador único de la orden a cancelar.

    Returns:
        Una respuesta estandarizada de éxito o error.
    """
    todas_las_ordenes = cargar_ordenes_pendientes()
    orden_a_cancelar = next((o for o in todas_las_ordenes if o.get("id_orden") == id_orden), None)

    if not orden_a_cancelar:
        return crear_respuesta_error(f"No se encontró una orden con el ID {id_orden}.")

    estado_actual = orden_a_cancelar.get("estado")
    if estado_actual != config.ESTADO_PENDIENTE:
        mensaje = f"La orden {id_orden} no puede ser cancelada porque su estado es '{estado_actual}', no '{config.ESTADO_PENDIENTE}'."
        return crear_respuesta_error(mensaje)

    billetera = cargar_billetera()
    moneda_reservada = orden_a_cancelar["moneda_reservada"]
    cantidad_reservada = a_decimal(orden_a_cancelar["cantidad_reservada"])

    activo_en_billetera = billetera.get(moneda_reservada)

    # Verificación de consistencia: se asegura de que los fondos reservados en la
    # billetera sean suficientes para cubrir la cantidad que la orden dice tener reservada.
    # Si no, marca la orden con un error para investigación manual.
    if not activo_en_billetera or a_decimal(activo_en_billetera.get("saldos", {}).get("reservado", Decimal('0'))) < cantidad_reservada:
        orden_a_cancelar["estado"] = config.ESTADO_ERROR
        orden_a_cancelar["mensaje_error"] = "Error de consistencia: los fondos a liberar no coinciden con la billetera."
        guardar_ordenes_pendientes(todas_las_ordenes)
        return crear_respuesta_error(orden_a_cancelar["mensaje_error"])

    # 2. Liberar fondos: se revierte la reserva en la billetera.
    activo_en_billetera["saldos"]["reservado"] -= cantidad_reservada
    activo_en_billetera["saldos"]["disponible"] += cantidad_reservada

    # 3. Actualizar estado de la orden.
    orden_a_cancelar["estado"] = config.ESTADO_CANCELADA
    orden_a_cancelar["timestamp_cancelacion"] = datetime.now().isoformat()

    # 4. Persistir todos los cambios de estado.
    guardar_ordenes_pendientes(todas_las_ordenes)
    guardar_billetera(billetera)

    # 5. Construir y devolver una respuesta clara para el frontend.
    # Se incluye el estado completo del activo modificado para que la UI
    # pueda refrescarse sin necesidad de una nueva llamada.
    mensaje_exito = f"Orden {orden_a_cancelar['par']} cancelada. Se liberaron {formato_cantidad_cripto(cantidad_reservada)} {moneda_reservada}."
    
    billetera_actualizada_completa = estado_actual_completo()
    activo_modificado = next((a for a in billetera_actualizada_completa if a['ticker'] == moneda_reservada), None)

    datos_exito = {
        "orden_cancelada": orden_a_cancelar,
        "activo_actualizado": activo_modificado
    }
    return crear_respuesta_exitosa(datos_exito, mensaje_exito)