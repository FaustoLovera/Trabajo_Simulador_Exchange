from flask import Blueprint, jsonify, render_template
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko
from backend.acceso_datos.datos_cotizaciones import cargar_datos_cotizaciones
from config import VELAS_PATH
import json

bp = Blueprint("api_externa", __name__, url_prefix="/api")


@bp.route("/actualizar")
def actualizar():
    """Actualiza los datos de criptomonedas desde CoinGecko."""
    datos = obtener_datos_criptos_coingecko()
    return jsonify({"estado": "ok", "cantidad": len(datos)})


@bp.route("/cotizaciones")
def get_cotizaciones():
    """Retorna la lista completa de cotizaciones en formato JSON."""
    return jsonify(cargar_datos_cotizaciones())


@bp.route("/velas")
def obtener_datos_velas():
    """Retorna los datos de velas desde un archivo JSON."""
    try:
        with open(VELAS_PATH, "r") as archivo:
            datos = json.load(archivo)
        return jsonify(datos)
    except (FileNotFoundError, IOError, json.JSONDecodeError) as e:
        print("❌ Error leyendo datos_velas.json:", e)
        return jsonify({"error": "No se pudo leer el archivo"}), 500