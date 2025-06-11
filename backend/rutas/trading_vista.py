from flask import Blueprint, request, redirect, url_for, render_template, flash
from backend.servicios.trading_logica import procesar_operacion_trading
from backend.servicios.velas_logica import cargar_datos_cotizaciones
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_historial import cargar_historial
from backend.servicios.api_cotizaciones import obtener_velas_binance
from backend.servicios.estado_billetera import estado_actual_completo
from decimal import Decimal, InvalidOperation

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
    raw_all_cryptos_data = cargar_datos_cotizaciones()
    print(f"DEBUG: Raw all_cryptos_data (from cargar_datos_cotizaciones): {raw_all_cryptos_data}") # DEBUG
    
    criptos_for_template = []
    for c in raw_all_cryptos_data:
        # Check if 'c' is actually a dictionary before using .get()
        if isinstance(c, dict):
            criptos_for_template.append({
                'ticker': c.get('ticker'),
                'nombre': c.get('nombre'),
                'precio_usdt': c.get('precio_usdt', Decimal('0.0')) 
            })
        else:
            print(f"ERROR: Element in all_cryptos_data is not a dict: {c} (Type: {type(c)})") # DEBUG for non-dict
            # Optionally, skip or handle this non-dict element more robustly
            continue # Skip this malformed element
    print(f"DEBUG: Processed criptos_for_template: {criptos_for_template}") # DEBUG
    
    estado = cargar_billetera() 
    print(f"DEBUG: Raw estado (from cargar_billetera): {estado}") # DEBUG
    
    raw_full_wallet_holdings = estado_actual_completo() 
    print(f"DEBUG: Raw full_wallet_holdings (from estado_actual_completo): {raw_full_wallet_holdings}") # DEBUG
    
    datos_for_template = []
    for d in raw_full_wallet_holdings:
        if isinstance(d, dict): # Check if 'd' is actually a dictionary
            if d.get("cantidad") is not None and Decimal(d.get("cantidad", '0.0')) > 0: # Use .get for 'cantidad' too for safety
                datos_for_template.append({
                    'ticker': d.get('ticker'),
                    'cantidad': d.get('cantidad'),
                    'precio_usdt': d.get('precio_usdt', Decimal('0.0')) 
                })
        else:
            print(f"ERROR: Element in full_wallet_holdings is not a dict: {d} (Type: {type(d)})") # DEBUG for non-dict
            # Optionally, skip or handle this non-dict element more robustly
            continue # Skip this malformed element
    print(f"DEBUG: Processed datos_for_template (held cryptos): {datos_for_template}") # DEBUG

    usdt_in_datos = any(d['ticker'] == 'USDT' for d in datos_for_template)
    if not usdt_in_datos and estado.get('USDT'):
        # Ensure 'estado.get('USDT')' returns a value that can be converted to Decimal
        usdt_balance = estado.get('USDT', '0.0') # Default to string '0.0' for Decimal conversion
        try:
            Decimal(usdt_balance) # Attempt conversion to catch errors early
            datos_for_template.append({
                'ticker': 'USDT',
                'cantidad': usdt_balance,
                'precio_usdt': Decimal('1.0') 
            })
        except InvalidOperation:
            print(f"ERROR: USDT balance '{usdt_balance}' from estado.get('USDT') is not a valid decimal.") # DEBUG
    
    print(f"DEBUG: Final datos_for_template (including USDT if added): {datos_for_template}") # DEBUG

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
        criptos=criptos_for_template,  
        estado=estado,
        historial=historial,
        datos=datos_for_template       
    )