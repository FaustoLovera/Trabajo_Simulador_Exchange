from flask import Blueprint, jsonify, render_template
import os 
import json
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko, obtener_velas_binance
from backend.acceso_datos.datos_cotizaciones import cargar_datos_cotizaciones
from config import VELAS_PATH


bp = Blueprint("api_externa", __name__, url_prefix="/api")


@bp.route("/actualizar")
def actualizar():
    """Actualiza los datos de criptomonedas y velas desde las APIs externas."""
    # ---> AÑADE ESTA LÍNEA EXACTAMENTE AQUÍ <---
    print("--- PING: Endpoint /api/actualizar ALCANZADO ---") 
    
    datos_criptos = obtener_datos_criptos_coingecko()
    obtener_velas_binance()
    return jsonify({"estado": "ok", "cantidad_criptos": len(datos_criptos)})


@bp.route("/cotizaciones")
def get_cotizaciones():
    """Retorna la lista completa de cotizaciones en formato JSON."""
    return jsonify(cargar_datos_cotizaciones())


@bp.route("/velas")
def obtener_datos_velas():
    """Retorna los datos de velas desde un archivo JSON de forma segura."""
    try:
        if not os.path.exists(VELAS_PATH) or os.path.getsize(VELAS_PATH) == 0:
            return jsonify([])

        with open(VELAS_PATH, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        return jsonify(datos)
    except (IOError, json.JSONDecodeError) as e:
        print("❌ Error leyendo datos_velas.json:", e)
        return jsonify({"error": "No se pudo leer el archivo de velas"}), 500