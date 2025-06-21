from flask import Blueprint, render_template, jsonify
from backend.servicios.estado_billetera import estado_actual_completo, obtener_historial_formateado
from backend.acceso_datos.datos_historial import cargar_historial
from backend.acceso_datos.datos_billetera import cargar_billetera

bp = Blueprint("billetera", __name__)


@bp.route("/billetera")
def mostrar_billetera():
    """Renderiza la página principal de la billetera (el contenedor HTML)."""
    # Ya no pasamos datos porque JS los cargará.
    return render_template("billetera.html")


@bp.route("/api/billetera/estado-completo")
def get_estado_billetera_completo():
    """Devuelve el estado financiero detallado de la billetera en JSON."""
    datos = estado_actual_completo()
    # La conversión de Decimal a string ya se realiza en la capa de servicio.
    return jsonify(datos)


@bp.route("/api/historial")
def get_historial_transacciones():
    """Devuelve el historial completo y formateado de transacciones en JSON."""
    return jsonify(obtener_historial_formateado())