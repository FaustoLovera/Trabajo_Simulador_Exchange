from flask import Blueprint, render_template, jsonify
from decimal import Decimal, ROUND_DOWN
from backend.servicios.estado_billetera import estado_actual_completo
from acceso_datos.datos_historial import cargar_historial
from acceso_datos.datos_billetera import cargar_datos_billetera as cargar_billetera

bp = Blueprint("billetera", __name__)

@bp.route("/billetera")
def mostrar_billetera():
    datos_billetera = estado_actual_completo()
    return render_template("billetera.html", datos=datos_billetera)

@bp.route("/estado")
def estado():
    return jsonify(cargar_billetera())


# Fragmento billetera API
@bp.route("/api/billetera")
def render_fragmento_billetera():
    datos = estado_actual_completo()
    for d in datos:
        d["color_ganancia"] = "green" if d["ganancia_perdida"] >= 0 else "red"
        d["color_porcentaje"] = "green" if d["porcentaje_ganancia"] >= 0 else "red"
    return render_template("fragmento_billetera.html", datos=datos)


# Fragmento historial API
@bp.route("/api/historial")
def render_fragmento_historial():
    historial = cargar_historial()
    for h in historial:
        h["color"] = "green" if h["tipo"] == "compra" else "red"
        h["cantidad"] = str(Decimal(h["cantidad"]).quantize(Decimal("0.00000001"), rounding=ROUND_DOWN))
    return render_template("fragmento_historial.html", historial=historial)