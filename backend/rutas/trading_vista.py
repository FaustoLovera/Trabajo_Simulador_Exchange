from flask import Blueprint, request, redirect, url_for, render_template, flash, json
from backend.servicios.trading_logica import procesar_operacion_trading
from backend.servicios.velas_logica import cargar_datos_cotizaciones
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_historial import cargar_historial
from backend.servicios.api_cotizaciones import obtener_velas_binance

bp = Blueprint("trading", __name__)

@bp.route("/trading", methods=["GET", "POST"])
def trading():
    """
    Gestiona las peticiones para la página de trading. Conecta la interfaz
    con la lógica de negocio.
    """
    if request.method == "POST":
        # Pasa los datos del formulario a la capa de lógica para ser procesados.
        exito, mensaje = procesar_operacion_trading(request.form)
        flash(mensaje, "success" if exito else "danger")
        return redirect(url_for("trading.trading"))

    # --- Lógica para la petición GET (mostrar la página) ---

    # 1. Actualiza los datos de mercado.
    obtener_velas_binance()

    # 2. Carga los datos necesarios para la plantilla.
    criptos_disponibles = cargar_datos_cotizaciones()
    billetera = cargar_billetera()
    historial = cargar_historial()
    monedas_propias_dict = {ticker: data for ticker, data in billetera.items() if data > 0}

    # 3. Prepara listas limpias para pasarlas a JSON y que JavaScript las pueda usar.
    lista_monedas_propias_js = [{'ticker': t, 'nombre': t} for t in monedas_propias_dict.keys()]
    # La lista de criptos disponibles ya tiene el formato correcto.

    # 4. Renderiza la plantilla con todos los datos necesarios.
    return render_template(
        "trading.html",
        criptos=criptos_disponibles,
        estado=billetera,
        monedas_propias=monedas_propias_dict,
        historial=historial,
        # Pasa las listas como strings JSON para que JavaScript las pueda leer
        lista_todas_las_criptos_json=json.dumps(criptos_disponibles),
        lista_monedas_propias_json=json.dumps(lista_monedas_propias_js)
    )