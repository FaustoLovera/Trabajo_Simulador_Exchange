"""
Define las rutas para la funcionalidad de trading.

Este módulo gestiona la visualización de la página de trading y el procesamiento
de las operaciones de compra y venta de criptomonedas enviadas por el usuario.
"""

from flask import Blueprint, request, redirect, url_for, render_template, flash
from backend.servicios.trading_logica import procesar_operacion_trading

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

    Recibe los datos del formulario enviado desde la página de trading, los pasa
    al servicio de lógica de trading para su procesamiento y muestra un mensaje
    (flash) al usuario con el resultado. Finalmente, redirige de vuelta a la
    página de trading.

    Side Effects:
        - Llama a `procesar_operacion_trading` para modificar el estado de la billetera.
        - Crea un mensaje flash para notificar al usuario.
        - Redirige al usuario a la página de trading.

    Returns:
        Response: Una redirección a la página de trading.
    """
    print(">>> DATOS RECIBIDOS DEL FORMULARIO:", request.form)

    exito, mensaje = procesar_operacion_trading(request.form)
    flash(mensaje, "success" if exito else "danger")

    # Siempre redirige de vuelta a la página principal de trading.
    return redirect(url_for("trading.mostrar_trading_page"))
