from decimal import Decimal
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_historial import cargar_historial
from backend.acceso_datos.datos_cotizaciones import obtener_precio, cargar_datos_cotizaciones
from backend.utils.formatters import formato_valor_monetario, formato_cantidad_cripto, formato_porcentaje, formato_fecha_hora

def calcular_detalle_cripto(ticker, cantidad_actual, precios, historial, info_cripto):
    # ... (Esta función no necesita cambios)
    cantidad_actual = Decimal(str(cantidad_actual))
    precio_actual = precios.get(ticker, Decimal("0"))
    valor_usdt = (cantidad_actual * precio_actual)

    compras = [
        op for op in historial
        if op.get("tipo") == "compra" and op.get("destino", {}).get("ticker") == ticker
    ]

    cantidad_comprada = sum(Decimal(str(op.get("destino", {}).get("cantidad", "0"))) for op in compras)
    total_invertido = sum(Decimal(str(op.get("valor_usd", "0"))) for op in compras)

    division_por_cero_segura = lambda num, den: num / den if den != 0 else Decimal("0")

    precio_promedio = division_por_cero_segura(total_invertido, cantidad_comprada)
    invertido_actual = cantidad_actual * precio_promedio
    ganancia = valor_usdt - invertido_actual
    porcentaje_ganancia = division_por_cero_segura(ganancia, invertido_actual) * Decimal("100")

    return {
        "ticker": ticker,
        "nombre": info_cripto.get('nombre', ticker),
        "cantidad": cantidad_actual,
        "valor_usdt": valor_usdt,
        "precio_actual": precio_actual,
        "precio_promedio": precio_promedio,
        "invertido": invertido_actual,
        "ganancia_perdida": ganancia,
        "porcentaje_ganancia": porcentaje_ganancia,
    }

def estado_actual_completo():
    billetera = cargar_billetera()
    historial = cargar_historial()
    
    todas_las_cotizaciones = cargar_datos_cotizaciones()
    info_map = {c.get('ticker'): c for c in todas_las_cotizaciones}
    
    precios = {ticker: obtener_precio(ticker) or Decimal("0") for ticker in billetera.keys()}

    detalles = []
    for ticker, cantidad in billetera.items():
        # ---> INICIO DE LA CORRECCIÓN PARA USDT <---
        if ticker == "USDT":
            # Caso especial para USDT: no está en la lista de Coingecko, así que le asignamos el nombre manualmente.
            info_cripto = {'nombre': 'Tether', 'ticker': 'USDT'}
        else:
            # Para todas las demás monedas, buscamos su información en el mapa.
            info_cripto = info_map.get(ticker, {'nombre': ticker}) # Fallback al ticker si no se encuentra
        # ---> FIN DE LA CORRECCIÓN <---

        detalle_calculado = calcular_detalle_cripto(ticker, cantidad, precios, historial, info_cripto)
        detalles.append(detalle_calculado)

    total_usdt = sum(d["valor_usdt"] for d in detalles if d["valor_usdt"] is not None)
    division_por_cero_segura = lambda num, den: num / den if den != 0 else Decimal("0")
    
    for detalle in detalles:
        porcentaje_billetera = division_por_cero_segura(detalle["valor_usdt"], total_usdt) * Decimal("100")
        
        detalle["porcentaje"] = porcentaje_billetera
        detalle["es_polvo"] = detalle["valor_usdt"] < Decimal("0.001")
        
        if detalle["ticker"] == 'USDT':
            detalle["cantidad_formatted"] = formato_valor_monetario(detalle["cantidad"], simbolo="")
        else:
            detalle["cantidad_formatted"] = formato_cantidad_cripto(detalle["cantidad"])
        
        detalle["precio_actual_formatted"] = formato_valor_monetario(detalle["precio_actual"], decimales=4)
        detalle["valor_usdt_formatted"] = formato_valor_monetario(detalle["valor_usdt"])
        detalle["ganancia_perdida_formatted"] = formato_valor_monetario(detalle["ganancia_perdida"])
        detalle["porcentaje_ganancia_formatted"] = formato_porcentaje(detalle["porcentaje_ganancia"])
        detalle["porcentaje_formatted"] = formato_porcentaje(porcentaje_billetera)

        for k, v in detalle.items():
            if isinstance(v, Decimal):
                detalle[k] = str(v)
    
    return detalles

def obtener_historial_formateado():
    """
    Carga el historial de transacciones y le añade campos formateados para la UI.
    """
    historial = cargar_historial()
    historial_formateado = []

    for item in historial:
        # Determinar detalles de la transacción
        if item.get('tipo') == 'compra':
            cantidad = Decimal(str(item.get('destino', {}).get('cantidad', '0')))
            par = f"{item.get('destino', {}).get('ticker', '?')}/{item.get('origen', {}).get('ticker', '?')}"
        else:  # Venta
            cantidad = Decimal(str(item.get('origen', {}).get('cantidad', '0')))
            par = f"{item.get('origen', {}).get('ticker', '?')}/{item.get('destino', {}).get('ticker', '?')}"

        item_formateado = item.copy()

        # Añadir campos formateados para la UI
        item_formateado['fecha_formatted'] = formato_fecha_hora(item.get('timestamp'))
        item_formateado['par_formatted'] = par
        item_formateado['tipo_formatted'] = item.get('tipo', '').capitalize()
        item_formateado['cantidad_formatted'] = formato_cantidad_cripto(cantidad)
        item_formateado['valor_total_formatted'] = formato_valor_monetario(Decimal(str(item.get('valor_usd', '0'))))

        # Convertir todos los Decimal a string para serialización JSON segura
        for k, v in item_formateado.items():
            if isinstance(v, Decimal):
                item_formateado[k] = str(v)
            elif isinstance(v, dict):
                v_copy = v.copy()
                for sub_k, sub_v in v_copy.items():
                    if isinstance(sub_v, Decimal):
                        v_copy[sub_k] = str(sub_v)
                item_formateado[k] = v_copy

        historial_formateado.append(item_formateado)

    return historial_formateado