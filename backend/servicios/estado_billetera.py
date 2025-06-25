# backend/servicios/estado_billetera.py
### VERSIÓN FINAL Y CORRECTA ###

from decimal import Decimal
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_historial import cargar_historial
from backend.acceso_datos.datos_cotizaciones import obtener_precio
from backend.utils.utilidades_numericas import (
    a_decimal, formato_cantidad_usd, formato_cantidad_cripto, formato_porcentaje
)
from backend.utils.formatters import format_datetime
from config import UMBRAL_POLVO_USD, UMBRAL_CASI_CERO

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

def _formatear_activo_para_presentacion(activo_calculado: dict, nombre: str, saldos: dict, total_billetera_usd: Decimal) -> dict:
    porcentaje_en_billetera = _division_segura(activo_calculado["valor_usdt"], total_billetera_usd) * Decimal("100")
    es_polvo = activo_calculado["valor_usdt"] < UMBRAL_POLVO_USD

    # Estoy probando si funciona sin esto:
    
    # if activo_calculado["ticker"] == 'USDT':
    #     cantidad_formateada = formato_cantidad_usd(activo_calculado["cantidad"], simbolo="")
    # else:
    #     cantidad_formateada = formato_cantidad_cripto(activo_calculado["cantidad"])
        
    cantidad_formateada = formato_cantidad_cripto(saldos.get("disponible", a_decimal(0)))

    return {
        "ticker": activo_calculado["ticker"], "nombre": nombre, "es_polvo": es_polvo,
        "cantidad": str(activo_calculado["cantidad"]),
        "cantidad_disponible": str(saldos.get("disponible", "0")),
        "cantidad_reservada": str(saldos.get("reservado", "0")),
        "cantidad_formatted": cantidad_formateada,
        "precio_actual_formatted": formato_cantidad_usd(activo_calculado["precio_actual"]),
        "valor_usdt_formatted": formato_cantidad_usd(activo_calculado["valor_usdt"]),
        "ganancia_perdida_formatted": formato_cantidad_usd(activo_calculado["ganancia_perdida"]),
        "ganancia_perdida_cruda": str(activo_calculado["ganancia_perdida"]),
        "porcentaje_ganancia_formatted": formato_porcentaje(activo_calculado["porcentaje_ganancia"]),
        "porcentaje_formatted": formato_porcentaje(porcentaje_en_billetera),
    }

def estado_actual_completo() -> list[dict]:
    billetera = cargar_billetera()
    historial = cargar_historial()
    datos_compra_por_ticker = _preparar_datos_compra(historial)

    activos_calculados = []
    # ### INICIO DE LA CORRECCIÓN ###
    # Iteramos sobre la nueva estructura de billetera
    for ticker, activo_data in billetera.items():
        saldos = activo_data.get("saldos", {}) # Obtenemos el diccionario de saldos
        
        cantidad_total = saldos.get("disponible", a_decimal(0)) + saldos.get("reservado", a_decimal(0))

        if cantidad_total < UMBRAL_CASI_CERO:
            continue
            
        if ticker == "USDT":
            metricas = {
                "ticker": "USDT", "cantidad": cantidad_total, "precio_actual": a_decimal(1),
                "valor_usdt": cantidad_total, "ganancia_perdida": a_decimal(0),
                "porcentaje_ganancia": a_decimal(0),
            }
        else:
            precio_actual = obtener_precio(ticker) or a_decimal(0)
            datos_compra_activo = datos_compra_por_ticker.get(ticker, {})
            metricas = _calcular_metricas_activo(ticker, cantidad_total, precio_actual, datos_compra_activo)
        
        # Añadimos los datos necesarios para el formateo
        metricas['nombre'] = activo_data.get('nombre', ticker)
        metricas['saldos'] = saldos
        activos_calculados.append(metricas)
    # ### FIN DE LA CORRECCIÓN ###

    total_billetera_usd = sum(activo["valor_usdt"] for activo in activos_calculados)

    activos_para_presentacion = [
        _formatear_activo_para_presentacion(activo, activo['nombre'], activo['saldos'], total_billetera_usd)
        for activo in activos_calculados
    ]
    return activos_para_presentacion

def obtener_historial_formateado() -> list[dict]:
    historial_crudo = cargar_historial()
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