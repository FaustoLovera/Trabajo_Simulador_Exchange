"""
Define las rutas relacionadas con la visualización de la billetera y el historial.

Este módulo contiene los endpoints para renderizar la página de la billetera
y para proporcionar datos financieros (estado actual y transacciones pasadas)
 a través de una API REST al frontend.
"""

from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from backend.servicios.estado_billetera import estado_actual_completo, obtener_historial_formateado
from backend.acceso_datos.datos_comisiones import cargar_comisiones
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes
from backend.servicios.trading.gestor import cancelar_orden_pendiente

bp = Blueprint("billetera", __name__)


@bp.route("/billetera")
def mostrar_billetera():
    """
    Renderiza la página principal de la billetera.

    Esta ruta sirve el archivo `billetera.html`, que actúa como el contenedor
    principal para la interfaz de la billetera. Los datos se cargan de forma
    asíncrona a través de llamadas a la API desde JavaScript.

    Returns:
        Response: El contenido HTML renderizado de la página de la billetera.
    """
    return render_template("billetera.html")


@bp.route("/api/billetera/estado-completo")
def get_estado_billetera_completo():
    """
    Endpoint de API que devuelve el estado financiero completo de la billetera.

    Proporciona un resumen detallado que incluye el balance de cada criptomoneda,
    su valor en USD, el total general, y el rendimiento.

    Returns:
        Response: Un objeto JSON con el estado completo de la billetera.
            Ejemplo: `{"total_usd": "10500.50", "rendimiento": "5.00", ...}`
    """
    datos = estado_actual_completo()
    return jsonify(datos)


@bp.route("/api/historial")
def get_historial_transacciones():
    """
    Endpoint de API que devuelve el historial completo de transacciones.

    Retorna una lista de todas las operaciones de compra y venta realizadas,
    formateadas para su visualización en el frontend.

    Returns:
        Response: Un objeto JSON que contiene una lista de transacciones.
            Ejemplo: `[{"id": 1, "fecha": "21/06/2025", "tipo": "compra", ...}]`
    """
    return jsonify(obtener_historial_formateado())

@bp.route("/api/comisiones")
def get_historial_comisiones():
    """
    Endpoint de API que devuelve el historial completo de comisiones cobradas.
    """
    return jsonify(cargar_comisiones())

@bp.route("/api/ordenes-abiertas")
def get_ordenes_abiertas():
    """
    Endpoint de API que devuelve la lista de órdenes que están pendientes de ejecución.
    """
    todas_las_ordenes = cargar_ordenes_pendientes()
    # Filtramos para devolver solo las que están activas
    ordenes_abiertas = [o for o in todas_las_ordenes if o.get("estado") == "pendiente"]
    return jsonify(ordenes_abiertas)

@bp.route("/api/orden/cancelar/<string:id_orden>", methods=["POST"])
def cancelar_orden_api(id_orden: str):
    """
    Endpoint de API para cancelar una orden pendiente.
    """
    exito, mensaje = cancelar_orden_pendiente(id_orden)
    
    # Usamos jsonify para una respuesta de API estándar
    if exito:
        return jsonify({"estado": "ok", "mensaje": mensaje}), 200
    else:
        return jsonify({"estado": "error", "mensaje": mensaje}), 400