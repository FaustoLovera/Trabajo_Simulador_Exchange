from flask import Blueprint, request, redirect, url_for, render_template, flash
from backend.servicios.trading_logica import procesar_operacion_trading
from backend.acceso_datos.datos_cotizaciones import cargar_datos_cotizaciones # Asegúrate de que esta sea la importación correcta
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
            # Aseguramos que 'cantidad' sea Decimal antes de la comparación
            cantidad_decimal = Decimal(str(d.get("cantidad", '0.0'))) 
            if cantidad_decimal > 0:
                datos_for_template.append({
                    'ticker': d.get('ticker'),
                    'cantidad': cantidad_decimal, # Ya es Decimal aquí
                    'precio_usdt': d.get('precio_usdt', Decimal('0.0')) 
                })
        else:
            print(f"ERROR: Element in full_wallet_holdings is not a dict: {d} (Type: {type(d)})")
            continue

    usdt_in_datos = any(d['ticker'] == 'USDT' for d in datos_for_template)
    if not usdt_in_datos and estado.get('USDT'):
        usdt_balance = estado.get('USDT', Decimal('0.0')) # Aseguramos que sea Decimal
        datos_for_template.append({
            'ticker': 'USDT',
            'cantidad': usdt_balance,
            'precio_usdt': Decimal('1.0') 
        })
    # Eliminar el bloque try-except InvalidOperation para usdt_balance ya que estado.get('USDT') ya debería ser Decimal.
    # Si aún hay problemas con el tipo de USDT en `estado`, la corrección debe hacerse en `cargar_billetera`.

    # Paso 3: Procesar formulario si es POST (sin cambios)
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
                cantidad_origen_calculada = (monto_usdt_a_vender / precio_origen_usdt).quantize(Decimal("0.00000001"))

                # Sobrescribir el modo-ingreso y el monto en los datos del formulario
                form_data["modo-ingreso"] = "cantidad_origen"
                form_data["monto"] = str(cantidad_origen_calculada) # Convertir a string para el formulario

            except InvalidOperation:
                flash("❌ El monto para la venta por valor no es un número válido.", "danger")
                return redirect(url_for("trading.trading"))
            except Exception as e:
                flash(f"❌ Error interno al procesar la venta por valor: {e}", "danger")
                return redirect(url_for("trading.trading"))
        
        exito, mensaje = procesar_operacion_trading(form_data)
        flash(mensaje, "success" if exito else "danger")
        return redirect(url_for("trading.trading"))

    # Paso 4: Cargar y TRANSFORMAR historial para la plantilla
    raw_historial = cargar_historial()
    historial_for_template = []

    for h in raw_historial:
        try:
            # 1. Determinar el color (ya lo hacías)
            color = "green" if h.get("tipo") == "compra" else "red"

            # 2. Determinar el Ticker principal de la operación (la cripto no USDT)
            parts = [p.strip() for p in h.get("par", " -> ").split("->")]
            ticker_display = ""
            if len(parts) == 2:
                if parts[0] == 'USDT':
                    ticker_display = parts[1]
                elif parts[1] == 'USDT':
                    ticker_display = parts[0]
                else: # Si no es un par con USDT, toma el primero (ej: BTC -> ETH, toma BTC)
                    ticker_display = parts[0] 
            
            # 3. Determinar la Cantidad relevante para mostrar
            # Cantidad de la cripto que fue el foco (lo que se compró o vendió)
            cantidad_origen_dec = Decimal(h.get('cantidad_origen', '0.0'))
            cantidad_destino_dec = Decimal(h.get('cantidad_destino', '0.0'))

            cantidad_display = Decimal('0.0')
            if h.get('tipo') == 'compra':
                # Si compras USDT->BTC, la cantidad relevante es BTC (cantidad_destino)
                cantidad_display = cantidad_destino_dec 
            elif h.get('tipo') == 'venta':
                # Si vendes BTC->USDT, la cantidad relevante es BTC (cantidad_origen)
                cantidad_display = cantidad_origen_dec
            
            # 4. Determinar el Monto en USDT
            # Monto de USDT involucrado en la transacción
            monto_usdt_display = Decimal('0.0')
            if h.get('tipo') == 'compra':
                # Si compras USDT->BTC, el monto USDT es lo que gastaste (cantidad_origen)
                monto_usdt_display = cantidad_origen_dec
            elif h.get('tipo') == 'venta':
                # Si vendes BTC->USDT, el monto USDT es lo que recibiste (cantidad_destino)
                monto_usdt_display = cantidad_destino_dec

            # 5. Determinar el Precio Unitario de la ejecución
            precio_unitario_display = Decimal(h.get('precio_ejecucion', '0.0'))

            historial_for_template.append({
                "fecha": h.get("fecha", ""),
                "tipo": h.get("tipo", ""),
                "color": color,
                "ticker": ticker_display,
                "cantidad": cantidad_display,
                "monto_usdt": monto_usdt_display,
                "precio_unitario": precio_unitario_display
            })
        except (InvalidOperation, KeyError, TypeError) as e:
            print(f"ERROR: No se pudo procesar item del historial '{h}'. Error: {e}")
            # Si un elemento no se puede procesar, puedes añadir un elemento de error o saltarlo.
            # Aquí lo añadimos con valores por defecto para evitar romper la plantilla.
            historial_for_template.append({
                "fecha": h.get("fecha", "N/A"),
                "tipo": h.get("tipo", "ERROR"),
                "color": "gray",
                "ticker": "ERROR",
                "cantidad": Decimal('0.0'),
                "monto_usdt": Decimal('0.0'),
                "precio_unitario": Decimal('0.0')
            })


    # DEBUG: Para verificar la estructura final del historial
    print(f"DEBUG trading_vista: Datos de historial formateados para plantilla: {historial_for_template}")

    # Paso 5: Renderizar plantilla
    return render_template(
        "trading.html",
        criptos=criptos_for_template,  
        estado=estado,
        historial=historial_for_template, # ¡Pasamos la lista transformada!
        datos=datos_for_template      
    )