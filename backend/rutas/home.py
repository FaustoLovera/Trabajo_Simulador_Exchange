from flask import Blueprint, render_template
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko
from backend.acceso_datos.datos_cotizaciones import recargar_cache_precios

bp = Blueprint("home", __name__)


@bp.route("/")
def index():
    """
    Página principal del simulador de exchange.
    """
    try:
        obtener_datos_criptos_coingecko()
        recargar_cache_precios()
        print("👉 Datos de cotizaciones actualizados.")
    except (KeyError, TypeError) as e:
        print(f"⚠️ Error al actualizar cotizaciones: {e}")
    
    return render_template("index.html")
