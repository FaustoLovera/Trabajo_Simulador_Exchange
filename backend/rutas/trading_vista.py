from flask import Blueprint, request, redirect, url_for, render_template, flash
from backend.servicios.trading_logica import procesar_operacion_trading
from backend.servicios.velas_logica import cargar_datos_cotizaciones
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_historial import cargar_historial
from backend.servicios.api_cotizaciones import obtener_velas_binance

bp = Blueprint("trading", __name__)

@bp.route("/trading", methods=["GET", "POST"])
def trading():
    """
    Vista principal de trading. Muestra las criptos disponibles, estado de billetera e historial.
    
    ---
    get:
      description: Muestra la interfaz de trading con datos actualizados.
      responses:
        200:
          description: Página de trading renderizada correctamente.
          content:
            text/html:
              example: "<html><body>Trading page</body></html>"

    post:
      description: Procesa una operación de compra o venta enviada por formulario.
      requestBody:
        content:
          application/x-www-form-urlencoded:
            schema:
              type: object
              properties:
                tipo:
                  type: string
                  example: "compra"
                ticker:
                  type: string
                  example: "BTC"
                cantidad:
                  type: string
                  example: "0.1"
      responses:
        302:
          description: Redirecciona tras procesar la operación con un mensaje flash.
    """
    obtener_velas_binance()
    criptos = cargar_datos_cotizaciones()
    estado = cargar_billetera()

    if request.method == "POST":
        exito, mensaje = procesar_operacion_trading(request.form)
        flash(mensaje, "success" if exito else "danger")
        return redirect(url_for("trading.trading"))

    historial = cargar_historial()
    for h in historial:
        h["color"] = "green" if h["tipo"] == "compra" else "red"
    return render_template("trading.html", criptos=criptos, estado=estado, historial=historial)
