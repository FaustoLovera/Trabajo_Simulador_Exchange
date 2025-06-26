# backend/rutas/trading_vista.py
### REFACTORIZADO ###

import json # Importamos la librería json
from flask import Blueprint, request, redirect, url_for, render_template, flash
from backend.servicios.trading.procesador import procesar_operacion_trading

bp = Blueprint("trading", __name__)

@bp.route("/trading", methods=["GET"])
def mostrar_trading_page():
    """ SIN CAMBIOS - Renderiza la página de trading. """
    return render_template("trading.html")

@bp.route("/trading/operar", methods=["POST"])
def procesar_trading_form():
    """
    ### REFACTORIZADO ###
    Procesa el formulario y pasa un JSON al sistema de flash en caso de éxito.
    """
    print(">>> DATOS RECIBIDOS DEL FORMULARIO:", request.form)

    ticker_operado = request.form.get("ticker", "BTC").upper()
    
    # Ahora 'mensaje' puede ser un diccionario o un string de error
    exito, mensaje = procesar_operacion_trading(request.form)

    if exito:
        # Si la operación fue exitosa, 'mensaje' es un diccionario.
        # Lo convertimos a un string JSON para guardarlo en la sesión flash.
        flash(json.dumps(mensaje), "success")
    else:
        # Si falló, 'mensaje' ya es un string de error.
        flash(mensaje, "danger")
    
    # La lógica de redirección no cambia.
    redirect_url = url_for("trading.mostrar_trading_page", ticker=ticker_operado)
    return redirect(redirect_url)