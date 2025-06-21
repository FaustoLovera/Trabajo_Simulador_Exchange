from flask import Blueprint, render_template, jsonify
from backend.servicios.estado_billetera import estado_actual_completo
from backend.acceso_datos.datos_historial import cargar_historial
from backend.acceso_datos.datos_billetera import cargar_billetera

bp = Blueprint("billetera", __name__)


@bp.route("/billetera")
def mostrar_billetera():
    """Renderiza la página principal de la billetera (el contenedor HTML)."""
    # Ya no pasamos datos porque JS los cargará.
    return render_template("billetera.html")


@bp.route("/estado")
def estado():
    """Devuelve el contenido actual de la billetera en formato JSON."""
    billetera_dict = {k: str(v) for k, v in cargar_billetera().items()}
    return jsonify(billetera_dict)

@bp.route("/api/billetera/estado-completo")
def get_estado_billetera_completo():
    """Devuelve el estado financiero detallado de la billetera en JSON."""
    datos = estado_actual_completo()
    # Convertimos los Decimal a string para que sean serializables en JSON
    for d in datos:
        for k, v in d.items():
            if hasattr(v, 'quantize'): # Es un Decimal
                d[k] = str(v)
    return jsonify(datos)


@bp.route("/api/historial")
def get_historial_transacciones():
    """Devuelve el historial completo de transacciones en JSON."""
    return jsonify(cargar_historial())