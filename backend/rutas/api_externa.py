from flask import Blueprint, jsonify
import json
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko, obtener_velas_de_api
from backend.acceso_datos.datos_cotizaciones import cargar_datos_cotizaciones
from config import VELAS_PATH

bp = Blueprint("api_externa", __name__, url_prefix="/api")


@bp.route("/actualizar")
def actualizar():
    """
    Actualiza SOLO los datos de cotizaciones de criptomonedas desde CoinGecko.
    Las velas ahora se obtienen bajo demanda.
    """
    print("--- PING: Endpoint /api/actualizar ALCANZADO ---") 
    datos_criptos = obtener_datos_criptos_coingecko()
    # Ya no llamamos a obtener_velas_binance() aquí.
    return jsonify({"estado": "ok", "cantidad_criptos": len(datos_criptos)})


@bp.route("/cotizaciones")
def get_cotizaciones():
    """Retorna la lista completa de cotizaciones en formato JSON."""
    return jsonify(cargar_datos_cotizaciones())


@bp.route("/velas/<string:ticker>/<string:interval>")
def obtener_datos_velas_por_ticker(ticker, interval):
    """
    Ruta dinámica que retorna datos de velas para un ticker y un intervalo.
    """
    try:
        datos = obtener_velas_de_api(ticker, interval)
        return jsonify(datos)
    except Exception as e:
        print(f"❌ Error en la ruta de velas para {ticker}/{interval}: {e}")
        return jsonify([])