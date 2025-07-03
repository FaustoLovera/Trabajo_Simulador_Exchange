"""Blueprint para las Rutas de la Interfaz de Trading.

Este módulo actúa como un **Controlador** en un patrón MVC. Su responsabilidad
es gestionar las peticiones HTTP relacionadas con la página de trading:
-   Renderiza la interfaz de usuario (`trading.html`).
-   Recibe los datos del formulario de operaciones (compra/venta).
-   Delega toda la lógica de negocio al `procesador` de servicios.
-   Comunica el resultado de la operación al usuario a través de mensajes flash.
"""

import json

from flask import Blueprint, render_template, request, flash, redirect, url_for

import config
from backend.servicios.trading.procesador import procesar_operacion_trading


# Define el Blueprint con el prefijo de URL `/trading`.
bp = Blueprint("trading", __name__, url_prefix="/trading")

@bp.route("/", methods=["GET"]) # Ruta -> /trading/
def mostrar_trading_page():
    """Renderiza la página principal de trading (`trading.html`).

    Esta vista simplemente sirve la plantilla HTML que contiene la interfaz
    de usuario para realizar operaciones. La carga de datos dinámicos (como
    cotizaciones o saldos) se realiza de forma asíncrona por el frontend.

    Returns:
        El contenido HTML renderizado de la página de trading.
    """
    return render_template("trading.html")


@bp.route("/operar", methods=["POST"]) # Ruta -> /trading/operar
def procesar_trading_form():
    """Endpoint para procesar los formularios de operaciones de trading.

    Este es el flujo de la operación:
    1.  Recibe los datos del formulario (`request.form`).
    2.  Delega la totalidad de la lógica de validación y ejecución al servicio
        `procesar_operacion_trading`, que actúa como la capa de negocio.
    3.  El servicio devuelve una respuesta estandarizada (un diccionario con
        `estado` y `datos` o `mensaje`).
    4.  Se utiliza el sistema de `flash` de Flask para enviar el resultado a la UI.
        - En caso de éxito, se pasa un JSON con los detalles de la operación.
        - En caso de error, se pasa un simple mensaje de texto.
    5.  Redirige al usuario de vuelta a la página de trading.

    Returns:
        Una redirección a la página de trading, conservando el ticker
        seleccionado para una mejor experiencia de usuario.
    """
    print(">>> DATOS RECIBIDOS DEL FORMULARIO:", request.form)

    ticker_operado = request.form.get(config.FORM_TICKER, "BTC").upper()

    # El servicio de procesamiento devuelve una respuesta estandarizada en un diccionario.
    respuesta = procesar_operacion_trading(request.form)

    if respuesta[config.RESPUESTA_ESTADO] == config.ESTADO_RESPUESTA_OK:
        # Si la operación fue exitosa, los datos de la transacción están en la clave 'datos'.
        # Se convierten a un string JSON para almacenarlos en el mensaje flash.
        flash(json.dumps(respuesta[config.RESPUESTA_DATOS]), config.FLASH_SUCCESS)
    else:
        # Si la operación falló, el motivo del error se encuentra en la clave 'mensaje'.
        flash(respuesta[config.RESPUESTA_MENSAJE], config.FLASH_DANGER)

        # Redirige de vuelta a la página de trading, pasando el ticker como
    # parámetro para que la interfaz pueda mostrar el mercado correcto.
    # Genera la URL de redirección de forma robusta usando constantes de `config.py`.
    # `url_for` crea la URL para el endpoint `ENDPOINT_TRADING_PAGE`.
    # El `**{...}` es una técnica para usar una constante (`FORM_TICKER`) como el nombre
    # del argumento de palabra clave, resultando en `...ticker=ticker_operado`.
    redirect_url = url_for(config.ENDPOINT_TRADING_PAGE, ticker=ticker_operado)
    return redirect(redirect_url)