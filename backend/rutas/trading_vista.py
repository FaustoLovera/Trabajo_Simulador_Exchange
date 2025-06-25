# backend/rutas/trading_vista.py (SIN CAMBIOS, YA ES CORRECTO)

"""
Define las rutas para la funcionalidad de trading.

Este módulo gestiona la visualización de la página de trading y el procesamiento
de las operaciones de compra y venta de criptomonedas enviadas por el usuario.
"""

from flask import Blueprint, request, redirect, url_for, render_template, flash
from backend.servicios.trading.procesador import procesar_operacion_trading

bp = Blueprint("trading", __name__)


@bp.route("/trading", methods=["GET"])
def mostrar_trading_page():
    """
    Renderiza la página de trading.

    Esta ruta maneja las solicitudes GET para mostrar la interfaz de trading,
    sirviendo el archivo `trading.html`.

    Returns:
        Response: El contenido HTML renderizado de la página de trading.
    """
    return render_template("trading.html")


@bp.route("/trading/operar", methods=["POST"])
def procesar_trading_form():
    """
    Procesa los datos del formulario de una operación de trading (compra/venta).

    Recibe los datos del formulario, los procesa y redirige de vuelta a la
    página de trading. Si la operación es exitosa, añade el ticker de la
    criptomoneda principal como parámetro en la URL para mantener el contexto.
    """
    print(">>> DATOS RECIBIDOS DEL FORMULARIO:", request.form)

    # Obtenemos el ticker principal de la operación desde el formulario.
    ticker_operado = request.form.get("ticker", "BTC").upper()

    # Se pasa el 'request.form' completo, que incluirá los nuevos campos cuando el frontend los envíe.
    exito, mensaje = procesar_operacion_trading(request.form)
    flash(mensaje, "success" if exito else "danger")
    
    # === LÓGICA DE REDIRECCIÓN INTELIGENTE ===
    if exito:
        # Si la operación fue exitosa, redirigimos a la página de trading
        # pasando el ticker que se operó como un parámetro en la URL.
        # Esto generará una URL como: /trading?ticker=ETH
        redirect_url = url_for("trading.mostrar_trading_page", ticker=ticker_operado)
    else:
        # Si falló, redirigimos manteniendo el último ticker visto para no perder el contexto.
        redirect_url = url_for("trading.mostrar_trading_page", ticker=ticker_operado)
    
    return redirect(redirect_url)