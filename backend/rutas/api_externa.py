from flask import Blueprint, jsonify, render_template
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko
from backend.servicios.cotizaciones import renderizar_fragmento_tabla
from config import VELAS_PATH
import json

bp = Blueprint("api_ruta", __name__)

@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/actualizar")
def actualizar():
    datos = obtener_datos_criptos_coingecko()
    return jsonify({"estado": "ok", "cantidad": len(datos)})

@bp.route("/datos_tabla")
def datos_tabla():
    return renderizar_fragmento_tabla()

@bp.route("/api/velas")
def obtener_datos_velas():
    try:
        with open(VELAS_PATH, "r") as archivo:
            datos = json.load(archivo)
        return jsonify(datos)
    except Exception as e:
        print("❌ Error leyendo datos_velas.json:", e)
        return jsonify({"error": "No se pudo leer el archivo"}), 500
