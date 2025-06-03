from flask import Blueprint, request, redirect, url_for, render_template, flash
from backend.servicios.trading_logica import procesar_operacion_trading
from backend.servicios.velas_logica import cargar_datos_cotizaciones
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_historial import cargar_historial
from backend.servicios.api_cotizaciones import obtener_velas_binance
from backend.servicios.estado_billetera import estado_actual_completo
from decimal import Decimal

bp = Blueprint("trading", __name__)

@bp.route("/trading", methods=["GET", "POST"])
def trading():
    """
    Vista principal de trading. Muestra las criptos disponibles, estado de billetera e historial.
    """

    print("🟢 Ruta /trading llamada")  # Para depuración

    # Paso 1: Actualizar velas si es necesario
    obtener_velas_binance()

    # Paso 2: Cargar datos necesarios
    criptos = cargar_datos_cotizaciones()               # Lista completa para "Destino"
    estado = cargar_billetera()                         # Billetera en crudo (JSON)
    billetera = estado_actual_completo()                # Lista detallada para "Origen"
    datos = [d for d in billetera if Decimal(d["cantidad"]) > 0]  # Solo con saldo

    # Paso 3: Procesar formulario si es POST
    if request.method == "POST":
        exito, mensaje = procesar_operacion_trading(request.form)
        flash(mensaje, "success" if exito else "danger")
        return redirect(url_for("trading.trading"))

    # Paso 4: Cargar historial
    historial = cargar_historial()
    for h in historial:
        h["color"] = "green" if h["tipo"] == "compra" else "red"

    # Paso 5: Renderizar plantilla
    return render_template(
        "trading.html",
        criptos=criptos,
        estado=estado,
        historial=historial,
        datos=datos  # 👈 PASAMOS ESTA VARIABLE AL TEMPLATE
    )
