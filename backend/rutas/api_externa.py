from flask import Blueprint, jsonify, render_template
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko
from backend.servicios.cotizaciones import renderizar_fragmento_tabla
from config import VELAS_PATH, COTIZACIONES_PATH
import json

bp = Blueprint("api_externa", __name__, url_prefix="/api")


@bp.route("/actualizar")
def actualizar():
    """
    Actualiza los datos de criptomonedas desde CoinGecko.
    ---
    responses:
      200:
        description: Devuelve estado ok y la cantidad de criptomonedas obtenidas.
        examples:
          application/json: { "estado": "ok", "cantidad": 50 }
    """
    datos = obtener_datos_criptos_coingecko()
    return jsonify({"estado": "ok", "cantidad": len(datos)})


@bp.route("/datos_tabla")
def datos_tabla():
    """
    Retorna el fragmento HTML de la tabla de cotizaciones.
    ---
    responses:
      200:
        description: Fragmento HTML de la tabla renderizado.
        content:
          text/html:
            example: "<tr><td>BTC</td><td>63500</td></tr>"
    """
    return renderizar_fragmento_tabla()


@bp.route("/velas")
def obtener_datos_velas():
    """
    Retorna los datos de velas desde un archivo JSON.
    ---
    responses:
      200:
        description: Datos de velas en formato JSON.
        content:
          application/json:
            example:
              [
                {"timestamp": 1714939200, "open": 65000, "close": 65500, "high": 66000, "low": 64500, "volume": 1200}
              ]
      500:
        description: Error al leer el archivo.
    """
    try:
        with open(VELAS_PATH, "r") as archivo:
            datos = json.load(archivo)
        return jsonify(datos)
    except Exception as e:
        print("❌ Error leyendo datos_velas.json:", e)
        return jsonify({"error": "No se pudo leer el archivo"}), 500
