from flask import Blueprint, request, redirect, url_for, render_template, flash
from backend.servicios.trading_logica import procesar_operacion_trading
from servicios.velas_logica import cargar_datos_cotizaciones
from acceso_datos.datos_billetera import cargar_billetera
from acceso_datos.datos_historial import cargar_historial
from backend.servicios.api_cotizaciones import obtener_velas_binance

bp = Blueprint("trading", __name__)

@bp.route("/trading", methods=["GET", "POST"])
def trading():
    obtener_velas_binance()
    criptos = cargar_datos_cotizaciones()
    estado = cargar_billetera()

    if request.method == "POST":
        exito, mensaje = procesar_operacion_trading(request.form)
        flash(mensaje, "success" if exito else "danger")
        return redirect(url_for("trading.trading"))

    historial = cargar_historial()
    for h in historial:
        h["color"] = "green" if h["tipo"] == "compra" else "red"
    return render_template("trading.html", criptos=criptos, estado=estado, historial=historial)
