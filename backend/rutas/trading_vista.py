# backend/rutas/trading_vista.py (VERSIÓN CON RUTAS SEPARADAS)

from flask import Blueprint, request, redirect, url_for, render_template, flash

from backend.servicios.trading_logica import procesar_operacion_trading

bp = Blueprint("trading", __name__)


# RUTA GET para MOSTRAR la página de trading
@bp.route("/trading", methods=["GET"])
def mostrar_trading_page():
    return render_template("trading.html")


# RUTA POST para PROCESAR la operación de trading
@bp.route("/trading/operar", methods=["POST"])
def procesar_trading_form():
    """Procesa los datos del formulario de trading."""
    
    print(">>> DATOS RECIBIDOS DEL FORMULARIO:", request.form)
    
    exito, mensaje = procesar_operacion_trading(request.form)
    flash(mensaje, "success" if exito else "danger")

    # Siempre redirige de vuelta a la página principal de trading
    return redirect(url_for("trading.mostrar_trading_page"))
