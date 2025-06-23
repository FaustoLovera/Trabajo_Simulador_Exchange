"""
Define los endpoints de la API externa de la aplicación.

Este módulo contiene las rutas que exponen datos del mercado de criptomonedas,
como cotizaciones y datos de velas (candlestick), para ser consumidos por el frontend
u otros clientes.
"""

from flask import Blueprint, jsonify
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko, obtener_velas_de_api
from backend.servicios.presentacion_datos import obtener_cotizaciones_formateadas

bp = Blueprint("api_externa", __name__, url_prefix="/api")


@bp.route("/actualizar")
def actualizar():
    """
    Endpoint para forzar la actualización de los datos de cotizaciones desde CoinGecko.

    Al ser llamado, este endpoint invoca al servicio que obtiene los precios más
    recientes de las criptomonedas y los guarda localmente.

    Returns:
        Response: Un objeto JSON que confirma el estado de la operación.
            Ejemplo: `{"estado": "ok", "cantidad_criptos": 100}`
    """
    print("--- PING: Endpoint /api/actualizar ALCANZADO ---")
    datos_criptos = obtener_datos_criptos_coingecko()
    return jsonify({"estado": "ok", "cantidad_criptos": len(datos_criptos)})


@bp.route("/cotizaciones")
def get_cotizaciones():
    """
    Retorna la lista completa de cotizaciones, formateada para la presentación.

    Esta ruta utiliza el servicio de presentación para tomar los datos crudos
    y enriquecerlos con formato antes de enviarlos al frontend.

    Returns:
        Response: Un objeto JSON que contiene una lista de todas las criptomonedas
                  y sus datos de cotización listos para ser mostrados.
                  Ejemplo: `[{"ticker": "BTC", "precio_usd_formatted": "$65,000.10", ...}]`
    """
    return jsonify(obtener_cotizaciones_formateadas())


@bp.route("/velas/<string:ticker>/<string:interval>")
def obtener_datos_velas_por_ticker(ticker: str, interval: str):
    """
    Obtiene los datos de velas (candlestick) para un par y un intervalo específicos.

    Esta ruta dinámica consulta a una API externa para obtener los datos históricos
    de precios (OHLCV) necesarios para graficar las velas.

    Args:
        ticker (str): El símbolo del par a consultar (ej. "BTCUSDT").
        interval (str): El intervalo de tiempo para las velas (ej. "1h", "4h", "1d").

    Returns:
        Response: Un objeto JSON con una lista de listas, donde cada sublista
                  representa una vela. En caso de error, retorna una lista vacía.
                  Ejemplo: `[[1622505600000, "49000.00", ...], ...]`
    """
    try:
        datos = obtener_velas_de_api(ticker, interval)
        return jsonify(datos)
    except Exception as e:
        print(f"❌ Error en la ruta de velas para {ticker}/{interval}: {e}")
        return jsonify([])