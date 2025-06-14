from flask import Blueprint, request, redirect, url_for, render_template, flash
from backend.servicios.trading_logica import procesar_operacion_trading
from backend.servicios.velas_logica import cargar_datos_cotizaciones
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_historial import cargar_historial
from backend.servicios.api_cotizaciones import obtener_velas_binance
from backend.servicios.estado_billetera import estado_actual_completo
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from decimal import Decimal, InvalidOperation

bp = Blueprint("trading", __name__)

@bp.route("/trading", methods=["GET", "POST"])
def trading():
    """
    Vista principal de trading. Muestra las criptos disponibles, estado de billetera e historial.
    """
    # Paso 1: Actualizar velas si es necesario
    obtener_velas_binance() 

    # Paso 2: Cargar datos necesarios (sin cambios en esta sección)
    raw_all_cryptos_data = cargar_datos_cotizaciones()
    
    criptos_for_template = []
    for c in raw_all_cryptos_data:
        if isinstance(c, dict):
            criptos_for_template.append({
                'ticker': c.get('ticker'),
                'nombre': c.get('nombre'),
                'precio_usdt': c.get('precio_usdt', Decimal('0.0')) 
            })
        else:
            print(f"ERROR: Element in all_cryptos_data is not a dict: {c} (Type: {type(c)})")
            continue
    
    estado = cargar_billetera() 
    
    raw_full_wallet_holdings = estado_actual_completo() 
    
    datos_for_template = []
    for d in raw_full_wallet_holdings:
        if isinstance(d, dict):
            if d.get("cantidad") is not None and Decimal(d.get("cantidad", '0.0')) > 0:
                datos_for_template.append({
                    'ticker': d.get('ticker'),
                    'cantidad': d.get('cantidad'),
                    'precio_usdt': d.get('precio_usdt', Decimal('0.0')) 
                })
        else:
            print(f"ERROR: Element in full_wallet_holdings is not a dict: {d} (Type: {type(d)})")
            continue

    usdt_in_datos = any(d['ticker'] == 'USDT' for d in datos_for_template)
    if not usdt_in_datos and estado.get('USDT'):
        usdt_balance = estado.get('USDT', '0.0')
        try:
            Decimal(usdt_balance)
            datos_for_template.append({
                'ticker': 'USDT',
                'cantidad': usdt_balance,
                'precio_usdt': Decimal('1.0') 
            })
        except InvalidOperation:
            print(f"ERROR: USDT balance '{usdt_balance}' from estado.get('USDT') is not a valid decimal.")

    # Paso 3: Procesar formulario si es POST
    if request.method == "POST":
        # Crea una copia mutable de los datos del formulario
        form_data = request.form.to_dict()

        accion_tipo = form_data.get("accion_tipo")
        modo_ingreso = form_data.get("modo-ingreso")
        origen_cripto = form_data.get("origen", "").upper()
        monto_str = form_data.get("monto")

        # Lógica para manejar la "venta por valor_usdt_origen"
        if accion_tipo == "venta" and modo_ingreso == "valor_usdt_origen":
            try:
                monto_usdt_a_vender = Decimal(monto_str)
                
                # Obtener el precio de la cripto de origen en USDT
                precio_origen_usdt = obtener_precio(origen_cripto)

                if precio_origen_usdt is None or precio_origen_usdt == Decimal("0"):
                    flash(f"❌ No se pudo obtener el precio de {origen_cripto} para la venta por valor.", "danger")
                    return redirect(url_for("trading.trading"))

                # Calcular la cantidad de la cripto de origen que corresponde al valor en USDT
                # cantidad_origen = valor_en_USDT / precio_de_origen_en_USDT
                cantidad_origen_calculada = (monto_usdt_a_vender / precio_origen_usdt).quantize(Decimal("0.00000001"))

                # Sobrescribir el modo-ingreso y el monto en los datos del formulario
                # para que procesar_operacion_trading lo entienda como "cantidad_origen"
                form_data["modo-ingreso"] = "cantidad_origen"
                form_data["monto"] = str(cantidad_origen_calculada) # Convertir a string para el formulario
                # El destino ya es USDT y la accion_tipo ya es venta, no necesitan ser cambiados

            except InvalidOperation:
                flash("❌ El monto para la venta por valor no es un número válido.", "danger")
                return redirect(url_for("trading.trading"))
            except Exception as e:
                flash(f"❌ Error interno al procesar la venta por valor: {e}", "danger")
                return redirect(url_for("trading.trading"))
        
        # Ahora, `form_data` contiene la `cantidad_origen` calculada si fue una venta por valor,
        # o los datos originales si no lo fue.
        exito, mensaje = procesar_operacion_trading(form_data)
        flash(mensaje, "success" if exito else "danger")
        return redirect(url_for("trading.trading"))

    # Paso 4: Cargar historial (sin cambios)
    historial = cargar_historial()
    for h in historial:
        h["color"] = "green" if h["tipo"] == "compra" else "red"

    # Paso 5: Renderizar plantilla (sin cambios)
    return render_template(
        "trading.html",
        criptos=criptos_for_template,  
        estado=estado,
        historial=historial,
        datos=datos_for_template      
    )