# backend/servicios/estado_billetera.py

from decimal import Decimal, InvalidOperation
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_cotizaciones import cargar_datos_cotizaciones
from backend.acceso_datos.datos_historial import cargar_historial

# ... (mantén la función calcular_detalle_cripto tal como la dejamos, con 'ganancia_o_perdida' y 'porcentaje_ganancia') ...
def calcular_detalle_cripto(ticker, cantidad, precios_usdt, historial):
    # print(f"DEBUG calcular_detalle_cripto: Recibido ticker='{ticker}', cantidad='{cantidad}', tipo(cantidad)={type(cantidad)}") # DEBUG
    precio_usdt = precios_usdt.get(ticker, Decimal('0.0'))
    # print(f"DEBUG calcular_detalle_cripto: precio_usdt='{precio_usdt}', tipo(precio_usdt)={type(precio_usdt)}") # DEBUG
    
    valor_usdt = cantidad * precio_usdt

    compras_relevantes = [
        op for op in historial 
        if op["tipo"] == "compra" and op["par"].split(" -> ")[1].strip() == ticker
    ]

    costo_total = Decimal('0.0')
    cantidad_total_comprada = Decimal('0.0')

    for op in compras_relevantes:
        try:
            costo_de_esta_compra = Decimal(op["cantidad_origen"]) # USDT gastado
            cantidad_comprada_en_esta_op = Decimal(op["cantidad_destino"]) # Cripto obtenida

            costo_total += costo_de_esta_compra
            cantidad_total_comprada += cantidad_comprada_en_esta_op
        except (ValueError, KeyError, InvalidOperation) as e:
            print(f"Advertencia: Error al procesar operación de historial: {op}. Error: {e}")
            continue 

    costo_promedio = (costo_total / cantidad_total_comprada).quantize(Decimal("0.00000001")) \
                     if cantidad_total_comprada > 0 else Decimal('0.0')

    ganancia_o_perdida = valor_usdt - (cantidad * costo_promedio)

    porcentaje_ganancia = Decimal('0.0')
    costo_posicion_actual = cantidad * costo_promedio 

    if costo_posicion_actual > 0:
        porcentaje_ganancia = (ganancia_o_perdida / costo_posicion_actual * Decimal('100')).quantize(Decimal("0.01"))
    elif cantidad > 0 and costo_promedio == Decimal('0.0'):
        if valor_usdt > 0:
            porcentaje_ganancia = Decimal('100.00')
        else:
            porcentaje_ganancia = Decimal('0.00')

    return {
        "ticker": ticker,
        "cantidad": cantidad,
        "precio_usdt": precio_usdt,
        "valor_usdt": valor_usdt,
        "costo_promedio": costo_promedio,
        "ganancia_o_perdida": ganancia_o_perdida,
        "porcentaje_ganancia": porcentaje_ganancia
    }


def estado_actual_completo():
    billetera = cargar_billetera()
    cotizaciones = cargar_datos_cotizaciones()
    historial = cargar_historial()

    precios_actuales = {c['ticker']: c['precio_usdt'] for c in cotizaciones}

    detalle_criptos = []
    total_portafolio_usdt = Decimal('0.0')

    # Excluir USDT de la iteración inicial, se manejará por separado
    # Asegúrate de que las cantidades de la billetera sean Decimal desde el principio
    criptos_en_billetera = {}
    for ticker, cantidad_str in billetera.items():
        try:
            criptos_en_billetera[ticker] = Decimal(cantidad_str)
        except InvalidOperation:
            print(f"Advertencia: Cantidad inválida '{cantidad_str}' para {ticker} en billetera. Se usa 0.0.")
            criptos_en_billetera[ticker] = Decimal('0.0')


    for ticker, cantidad_decimal in criptos_en_billetera.items():
        if ticker == 'USDT':
            # USDT se maneja de forma especial, no tiene ganancia/pérdida o costo promedio en este contexto
            # Solo se añade su valor directo al total del portafolio.
            if cantidad_decimal > 0:
                detalle_criptos.append({
                    "ticker": "USDT",
                    "cantidad": cantidad_decimal,
                    "precio_usdt": Decimal('1.0'), # El precio de USDT es 1
                    "valor_usdt": cantidad_decimal, # El valor de USDT es su propia cantidad
                    "costo_promedio": Decimal('1.0'), # Asumimos 1 para USDT en promedio
                    "ganancia_o_perdida": Decimal('0.0'), # USDT no tiene ganancia/pérdida
                    "porcentaje_ganancia": Decimal('0.0') # USDT no tiene porcentaje de ganancia
                })
                total_portafolio_usdt += cantidad_decimal
            continue # Saltamos al siguiente elemento si es USDT

        # Para otras criptos (no USDT)
        if cantidad_decimal > 0: 
            try:
                detalle = calcular_detalle_cripto(ticker, cantidad_decimal, precios_actuales, historial)
                detalle_criptos.append(detalle)
                total_portafolio_usdt += detalle['valor_usdt']
            except Exception as e:
                print(f"Error calculando detalle para {ticker}: {e}")
        else:
             # Si la cantidad es 0, también podemos añadirla para que aparezca en la lista,
             # pero con valores de 0 en el detalle, si se desea.
             # Si no quieres ver las criptos con 0, puedes eliminar este else.
             detalle_criptos.append({
                 "ticker": ticker,
                 "cantidad": Decimal('0.0'),
                 "precio_usdt": precios_actuales.get(ticker, Decimal('0.0')),
                 "valor_usdt": Decimal('0.0'),
                 "costo_promedio": Decimal('0.0'),
                 "ganancia_o_perdida": Decimal('0.0'),
                 "porcentaje_ganancia": Decimal('0.0')
             })


    # ¡NUEVO BLOQUE! Calcular el porcentaje de cada cripto en el portafolio total
    for cripto_detalle in detalle_criptos:
        porcentaje_en_billetera = Decimal('0.0')
        if total_portafolio_usdt > 0:
            porcentaje_en_billetera = (cripto_detalle['valor_usdt'] / total_portafolio_usdt * Decimal('100')).quantize(Decimal("0.01"))
        
        # Asignar el porcentaje calculado a la nueva clave 'porcentaje'
        cripto_detalle['porcentaje'] = porcentaje_en_billetera 

    print(f"DEBUG estado_actual_completo: Datos finales de billetera para plantilla: {detalle_criptos}") # Para depuración
    return detalle_criptos