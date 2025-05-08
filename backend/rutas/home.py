from flask import Blueprint, render_template
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko

bp = Blueprint("home", __name__)

@bp.route("/")
def index():
    try:
        obtener_datos_criptos_coingecko()
        print("👉 Finalizó la obtención de datos.")
    except Exception as e:
        print(f"⚠️ Error al obtener datos: {e}")
    return render_template("index.html")