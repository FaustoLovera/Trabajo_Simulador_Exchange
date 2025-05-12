from flask import Blueprint, render_template, jsonify
from decimal import Decimal, ROUND_DOWN
from backend.servicios.estado_billetera import estado_actual_completo
from backend.acceso_datos.datos_historial import cargar_historial
from backend.acceso_datos.datos_billetera import cargar_billetera

bp = Blueprint("billetera", __name__)

@bp.route("/billetera")
def mostrar_billetera():
    """
    Muestra el estado completo de la billetera en una tabla HTML.
    ---
    responses:
      200:
        description: Renderiza la vista de billetera.
        content:
          text/html:
            example: "<table><tr><td>BTC</td><td>0.5</td></tr></table>"
    """
    datos_billetera = estado_actual_completo()
    return render_template("billetera.html", datos=datos_billetera)


@bp.route("/estado")
def estado():
    """
    Devuelve el contenido actual de la billetera en formato JSON.
    ---
    responses:
      200:
        description: JSON con los saldos actuales.
        content:
          application/json:
            example: { "BTC": 0.5, "ETH": 2.0 }
    """
    return jsonify(cargar_billetera())


@bp.route("/api/billetera")
def render_fragmento_billetera():
    """
    Devuelve un fragmento HTML con los datos detallados de la billetera.
    ---
    responses:
      200:
        description: Fragmento HTML renderizado con estilo de ganancia/pérdida.
        content:
          text/html:
            example: "<tr><td>BTC</td><td style='color:green'>+5%</td></tr>"
    """
    datos = estado_actual_completo()
    for d in datos:
        d["color_ganancia"] = "green" if d["ganancia_perdida"] >= 0 else "red"
        d["color_porcentaje"] = "green" if d["porcentaje_ganancia"] >= 0 else "red"
    return render_template("fragmento_billetera.html", datos=datos)


@bp.route("/api/historial")
def render_fragmento_historial():
    """
    Devuelve un fragmento HTML con el historial de transacciones.
    ---
    responses:
      200:
        description: Fragmento HTML con historial de compras y ventas.
        content:
          text/html:
            example: "<tr><td>compra</td><td>BTC</td><td>0.1</td></tr>"
    """
    historial = cargar_historial()
    for h in historial:
        h["color"] = "green" if h["tipo"] == "compra" else "red"
        h["cantidad"] = str(Decimal(h["cantidad"]).quantize(Decimal("0.00000001"), rounding=ROUND_DOWN))
    return render_template("fragmento_historial.html", historial=historial)