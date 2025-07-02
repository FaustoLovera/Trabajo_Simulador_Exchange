"""Blueprint para la API de Datos de Mercado y Disparador del Motor.

Este módulo actúa como un **Gateway** que expone datos de mercado al frontend.
Su rol más importante es el endpoint `/actualizar`, que funciona como el
**'heartbeat' (latido) del simulador**: no solo obtiene los precios más
recientes, sino que también dispara el motor de ejecución de órdenes pendientes.

Las otras rutas proveen datos ya procesados y formateados para la UI.
"""

from flask import Blueprint, jsonify
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko, obtener_velas_de_api
from backend.servicios.presentacion_datos import obtener_cotizaciones_formateadas

from backend.servicios.trading.motor import verificar_y_ejecutar_ordenes_pendientes

bp = Blueprint("api_externa", __name__, url_prefix="/api")


@bp.route("/actualizar")
def actualizar():
    """Endpoint 'Heartbeat': Actualiza precios y ejecuta el motor de órdenes.

    Esta es una de las rutas más importantes del sistema. El frontend la llama
    periódicamente para simular un mercado en tiempo real. Su flujo es:

    1.  **Obtener Datos Frescos**: Llama a `obtener_datos_criptos_coingecko` para
        actualizar la caché local de precios con los últimos datos del mercado.
    2.  **Activar el Motor**: Con los nuevos precios ya guardados, invoca a
        `verificar_y_ejecutar_ordenes_pendientes`, el corazón del motor de
        trading, para que evalúe y ejecute órdenes Stop-Limit pendientes.

    Returns:
        Una respuesta JSON simple confirmando que la actualización se completó.
    """
    print("--- PING: Endpoint /api/actualizar ALCANZADO ---")
    
    # 1. Obtener los datos más recientes de cotizaciones y guardarlos.
    datos_criptos = obtener_datos_criptos_coingecko()
    
    # --- 2. ¡ACTIVAR EL MOTOR DE EJECUCIÓN DE ÓRDENES! ---
    # Con los precios frescos en memoria, verificamos si alguna orden pendiente se cumple.
    verificar_y_ejecutar_ordenes_pendientes()
    
    # 3. Devolver la respuesta al frontend.
    return jsonify({"estado": "ok", "cantidad_criptos": len(datos_criptos)})


@bp.route("/cotizaciones")
def get_cotizaciones():
    """API Endpoint: Devuelve la lista de cotizaciones formateadas para la UI.

    Delega la tarea al servicio `obtener_cotizaciones_formateadas`, que se
    encarga de tomar los datos crudos, aplicarles formato legible para humanos
    y añadir indicadores de rendimiento visual.

    Returns:
        Una respuesta JSON con la lista de cotizaciones listas para presentar.
    """
    return jsonify(obtener_cotizaciones_formateadas())


@bp.route("/velas/<string:ticker>/<string:interval>")
def obtener_datos_velas_por_ticker(ticker: str, interval: str):
    """API Endpoint: Devuelve datos de velas (candlestick) para un activo.

    Actúa como un passthrough hacia el servicio `obtener_velas_de_api`, que
    se encarga de la comunicación con la API externa (Binance) para obtener
    los datos históricos necesarios para los gráficos de velas.

    Args:
        ticker: El símbolo del activo (ej. "BTC").
        interval: El intervalo de tiempo de las velas (ej. "1h", "4h", "1d").

    Returns:
        Una respuesta JSON con los datos para el gráfico o una lista vacía
        en caso de error.
    """
    try:
        datos = obtener_velas_de_api(ticker, interval)
        return jsonify(datos)
    except Exception as e:
        print(f"❌ Error en la ruta de velas para {ticker}/{interval}: {e}")
        return jsonify([])