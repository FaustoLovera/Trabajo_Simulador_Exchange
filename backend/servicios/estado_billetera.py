# backend/servicios/estado_billetera.py

from decimal import Decimal

from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_historial import cargar_historial
# Se elimina la importación de obtener_precio, ya que no se usará el caché global en los tests.
from backend.acceso_datos.datos_cotizaciones import cargar_datos_cotizaciones
from backend.utils.utilidades_numericas import (
    a_decimal, formato_cantidad_usd, formato_cantidad_cripto, formato_porcentaje
)
from backend.utils.formatters import format_datetime
from config import (
    UMBRAL_POLVO_USD, UMBRAL_CASI_CERO,
    BILLETERA_PATH, HISTORIAL_PATH, COTIZACIONES_PATH
)

def _division_segura(numerador: Decimal, denominador: Decimal) -> Decimal:
    return numerador / denominador if denominador > a_decimal(0) else a_decimal(0)

def _preparar_datos_compra(historial: list[dict]) -> dict[str, dict]:
    datos_compra_por_ticker = {}
    for operacion in historial:
        if operacion.get("tipo", "").endswith("compra"):
            destino = operacion.get("destino", {})
            ticker = destino.get("ticker")
            if not ticker or ticker == "USDT": continue
            if ticker not in datos_compra_por_ticker:
                datos_compra_por_ticker[ticker] = {"total_invertido": a_decimal(0), "cantidad_comprada": a_decimal(0)}
            datos_compra_por_ticker[ticker]["total_invertido"] += a_decimal(operacion.get("valor_usd"))
            datos_compra_por_ticker[ticker]["cantidad_comprada"] += a_decimal(destino.get("cantidad"))
    return datos_compra_por_ticker

def _calcular_metricas_activo(ticker: str, cantidad_total: Decimal, precio_actual: Decimal, datos_compra: dict) -> dict:
    valor_actual_usd = cantidad_total * precio_actual
    total_invertido = datos_compra.get("total_invertido", a_decimal(0))
    cantidad_comprada = datos_compra.get("cantidad_comprada", a_decimal(0))
    precio_promedio_compra = _division_segura(total_invertido, cantidad_comprada)
    costo_base_actual = cantidad_total * precio_promedio_compra
    ganancia_o_perdida = valor_actual_usd - costo_base_actual if costo_base_actual > 0 else a_decimal(0)
    porcentaje_ganancia = _division_segura(ganancia_o_perdida, costo_base_actual) * Decimal("100")
    return {
        "ticker": ticker, "cantidad": cantidad_total, "precio_actual": precio_actual,
        "valor_usdt": valor_actual_usd, "precio_promedio_compra": precio_promedio_compra,
        "costo_base_actual": costo_base_actual, "ganancia_perdida": ganancia_o_perdida,
        "porcentaje_ganancia": porcentaje_ganancia,
    }

def _formatear_activo_para_presentacion(activo_calculado: dict, cripto_info: dict, saldos: dict, total_billetera_usd: Decimal) -> dict:
    porcentaje_en_billetera = _division_segura(activo_calculado["valor_usdt"], total_billetera_usd) * Decimal("100")
    es_polvo = activo_calculado["valor_usdt"] < UMBRAL_POLVO_USD

    cantidad_total = activo_calculado["cantidad"]
    saldo_disponible = saldos.get("disponible", a_decimal(0))
    saldo_reservado = saldos.get("reservado", a_decimal(0))

    return {
        "ticker": activo_calculado["ticker"],
        "nombre": cripto_info.get("nombre", activo_calculado["ticker"]),
        "logo": cripto_info.get("logo", ""),
        "es_polvo": es_polvo,
        
        "cantidad_total": str(cantidad_total),
        "cantidad_disponible": str(saldo_disponible),
        "cantidad_reservada": str(saldo_reservado),

        "cantidad_total_formatted": formato_cantidad_cripto(cantidad_total),
        "cantidad_disponible_formatted": formato_cantidad_cripto(saldo_disponible),
        "cantidad_reservada_formatted": formato_cantidad_cripto(saldo_reservado),
        
        "precio_actual_formatted": formato_cantidad_usd(activo_calculado["precio_actual"]),
        "valor_usdt_formatted": formato_cantidad_usd(activo_calculado["valor_usdt"]),
        "ganancia_perdida_formatted": formato_cantidad_usd(activo_calculado["ganancia_perdida"]),
        "ganancia_perdida_cruda": str(activo_calculado["ganancia_perdida"]),
        "porcentaje_ganancia_formatted": formato_porcentaje(activo_calculado["porcentaje_ganancia"]),
        "porcentaje_formatted": formato_porcentaje(porcentaje_en_billetera),
    }

def estado_actual_completo(
    ruta_billetera: str = BILLETERA_PATH,
    ruta_historial: str = HISTORIAL_PATH,
    ruta_cotizaciones: str = COTIZACIONES_PATH
) -> list[dict]:
    billetera = cargar_billetera(ruta_archivo=ruta_billetera)
    historial = cargar_historial(ruta_archivo=ruta_historial)
    cotizaciones_raw = cargar_datos_cotizaciones(ruta_archivo=ruta_cotizaciones)
    
    info_criptos = {c['ticker']: c for c in cotizaciones_raw}
    precios_locales = {c['ticker']: a_decimal(c.get('precio_usd', '0')) for c in cotizaciones_raw}
    
    # ### LA SOLUCIÓN ESTÁ AQUÍ ###
    # Forzamos el nombre y logo canónicos para USDT, ignorando lo que venga de la API.
    # Esto asegura consistencia y evita nombres como "Polygon Bridged USDT".
    info_criptos['USDT'] = {
        'nombre': 'Tether', 
        'logo': 'https://assets.coingecko.com/coins/images/325/large/Tether.png?1696501661',
        'ticker': 'USDT'
    }

    datos_compra_por_ticker = _preparar_datos_compra(historial)
    activos_calculados = []
    
    for ticker, activo_data in billetera.items():
        saldos = activo_data.get("saldos", {})
        cantidad_total = saldos.get("disponible", a_decimal(0)) + saldos.get("reservado", a_decimal(0))

        if cantidad_total < UMBRAL_CASI_CERO:
            continue
            
        # Obtenemos la información de la cripto de nuestro diccionario 'curado'.
        cripto_info_actual = info_criptos.get(ticker, {"nombre": ticker, "logo": ""})

        if ticker == "USDT":
            metricas = {
                "ticker": "USDT", "cantidad": cantidad_total, "precio_actual": a_decimal(1),
                "valor_usdt": cantidad_total, "ganancia_perdida": a_decimal(0),
                "porcentaje_ganancia": a_decimal(0),
            }
        else:
            precio_actual = precios_locales.get(ticker, a_decimal(0))
            datos_compra_activo = datos_compra_por_ticker.get(ticker, {})
            metricas = _calcular_metricas_activo(ticker, cantidad_total, precio_actual, datos_compra_activo)
        
        metricas['cripto_info'] = cripto_info_actual
        metricas['saldos'] = saldos
        activos_calculados.append(metricas)

    activos_calculados.sort(key=lambda x: x['valor_usdt'], reverse=True)
    total_billetera_usd = sum(activo['valor_usdt'] for activo in activos_calculados)

    activos_para_presentacion = [
        _formatear_activo_para_presentacion(activo, activo['cripto_info'], activo['saldos'], total_billetera_usd)
        for activo in activos_calculados
    ]
    return activos_para_presentacion

def obtener_historial_formateado(ruta_historial: str = HISTORIAL_PATH) -> list[dict]:
    historial_crudo = cargar_historial(ruta_archivo=ruta_historial)
    historial_formateado = []
    for item in historial_crudo:
        tipo_op = item.get('tipo', '')
        par_origen = item.get('origen', {}).get('ticker', '?')
        par_destino = item.get('destino', {}).get('ticker', '?')
        cantidad = a_decimal(item.get('destino', {}).get('cantidad')) if tipo_op.endswith('compra') else a_decimal(item.get('origen', {}).get('cantidad'))
        item_formateado = {
            "id": item.get("id"), "tipo": tipo_op,
            "fecha_formatted": format_datetime(item.get('timestamp')),
            "par_formatted": f"{par_destino}/{par_origen}",
            "tipo_formatted": tipo_op.replace('-', ' ').capitalize(),
            "cantidad_formatted": formato_cantidad_cripto(cantidad),
            "valor_total_formatted": formato_cantidad_usd(a_decimal(item.get('valor_usd'))),
        }
        historial_formateado.append(item_formateado)
    return historial_formateado