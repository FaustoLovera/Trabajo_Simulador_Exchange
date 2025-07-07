"""Blueprint para todas las Rutas de la API RESTful.

Este módulo centraliza todos los endpoints que devuelven datos en formato JSON,
actuando como la capa de Controlador que responde a las peticiones asíncronas
del frontend (AJAX/Fetch).

Responsabilidades:
- Exponer datos del estado de la billetera, historial, comisiones y órdenes.
- Gestionar operaciones como la cancelación de órdenes.
- Delegar toda la lógica de negocio a la capa de `servicios`.
"""

from flask import Blueprint, jsonify
from backend.servicios.estado_billetera import estado_actual_completo, obtener_historial_formateado, obtener_comisiones_formateadas
from backend.acceso_datos.datos_ordenes import cargar_ordenes_pendientes
from backend.servicios.trading.gestor import cancelar_orden_pendiente
import config

# Define el Blueprint con el prefijo de URL `/api`.
# Todas las rutas definidas aquí comenzarán con /api.
bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/billetera/estado-completo")
def get_estado_billetera_completo():
    """API Endpoint: Devuelve el estado analítico completo del portafolio."""
    datos = estado_actual_completo()
    return jsonify(datos)


@bp.route("/historial")
def get_historial_transacciones():
    """API Endpoint: Devuelve el historial de transacciones formateado."""
    return jsonify(obtener_historial_formateado())


@bp.route("/comisiones")
def get_historial_comisiones():
    """API Endpoint: Devuelve el historial de comisiones cobradas."""
    return jsonify(obtener_comisiones_formateadas())


@bp.route("/ordenes-abiertas")
def get_ordenes_abiertas():
    """API Endpoint: Devuelve la lista de órdenes pendientes (abiertas)."""
    todas_las_ordenes = cargar_ordenes_pendientes()
    ordenes_abiertas = [o for o in todas_las_ordenes if o.get("estado") == config.ESTADO_PENDIENTE]
    return jsonify(ordenes_abiertas)


@bp.route("/orden/cancelar/<string:id_orden>", methods=["POST"])
def cancelar_orden_api(id_orden: str):
    """API Endpoint: Cancela una orden pendiente específica."""
    resultado = cancelar_orden_pendiente(id_orden)
    return jsonify(resultado)
