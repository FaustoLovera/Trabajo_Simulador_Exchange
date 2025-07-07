"""Servicio de Orquestación y Análisis del Estado de la Billetera.

Este módulo es un servicio de alto nivel que actúa como orquestador. Su
responsabilidad principal es consolidar datos de múltiples fuentes (billetera,
historial de transacciones, cotizaciones de mercado) para construir una vista
analítica y enriquecida del portafolio del usuario, lista para ser consumida
por el frontend.

El pipeline de datos es el siguiente:
1.  **Carga de Datos**: Lee los archivos JSON de billetera, historial y cotizaciones.
2.  **Procesamiento del Historial**: Calcula el costo base agregado para cada activo.
3.  **Cálculo de Métricas**: Para cada activo, calcula su valor actual, P/L, etc.
4.  **Formateo para Presentación**: Convierte todos los datos numéricos a cadenas
    formateadas y añade información útil para la UI (ej. logos, porcentajes).
"""

from decimal import Decimal
from typing import Any, Dict, List

from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_comisiones import cargar_comisiones
from backend.acceso_datos.datos_cotizaciones import cargar_datos_cotizaciones
from backend.acceso_datos.datos_historial import cargar_historial
from backend.utils.formatters import format_datetime
from backend.utils import utilidades_numericas
import config

def _division_segura(numerador: Decimal, denominador: Decimal) -> Decimal:
    """Divide dos números Decimal de forma segura, evitando errores de división por cero."""
    return numerador / denominador if denominador > utilidades_numericas.a_decimal(0) else utilidades_numericas.a_decimal(0)

def _preparar_datos_compra(
    historial: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Decimal]]:
    """Procesa el historial para calcular el costo base agregado de cada criptomoneda.

    Esta función es un paso clave en el pipeline. Itera sobre todas las
    transacciones y acumula el total de USD invertido y la cantidad de cripto
    adquirida por cada ticker. El resultado es fundamental para calcular el
    precio promedio de compra y, consecuentemente, la ganancia o pérdida.

    Args:
        historial: La lista completa de transacciones.

    Returns:
        Un diccionario que mapea cada ticker a su `total_invertido` y
        `cantidad_comprada` acumulados.
    """
    datos_compra_por_ticker: Dict[str, Dict[str, Decimal]] = {}
    for operacion in historial:
        if config.ACCION_COMPRAR in operacion.get("tipo", "").lower():
            destino = operacion.get("destino", {})
            ticker = destino.get("ticker")
            if not ticker or ticker == config.MONEDA_FIAT_DEFAULT:
                continue
            if ticker not in datos_compra_por_ticker:
                datos_compra_por_ticker[ticker] = {
                    "total_invertido": utilidades_numericas.a_decimal(0),
                    "cantidad_comprada": utilidades_numericas.a_decimal(0),
                }
            datos_compra_por_ticker[ticker]["total_invertido"] += utilidades_numericas.a_decimal(
                operacion.get("valor_usd")
            )
            datos_compra_por_ticker[ticker]["cantidad_comprada"] += utilidades_numericas.a_decimal(
                destino.get("cantidad")
            )
    return datos_compra_por_ticker

def _calcular_metricas_activo(
    ticker: str,
    cantidad_total: Decimal,
    precio_actual: Decimal,
    datos_compra: Dict[str, Decimal],
) -> Dict[str, Any]:
    """Calcula un conjunto completo de métricas de rendimiento para un activo.

    Esta función toma los datos brutos de un activo y los transforma en insights
    financieros, como el valor actual, el costo base, la ganancia/pérdida y su
    variación porcentual. Todos los cálculos se realizan con `Decimal` para
    mantener la precisión.

    Args:
        ticker: El ticker del activo (ej. "BTC").
        cantidad_total: La cantidad total del activo en la billetera.
        precio_actual: El precio de mercado actual del activo.
        datos_compra: Un diccionario con el `total_invertido` y `cantidad_comprada`.

    Returns:
        Un diccionario con todas las métricas calculadas, aún en formato `Decimal`.
    """
    valor_actual_usd = cantidad_total * precio_actual
    total_invertido = datos_compra.get("total_invertido", utilidades_numericas.a_decimal(0))
    cantidad_comprada = datos_compra.get("cantidad_comprada", utilidades_numericas.a_decimal(0))
    precio_promedio_compra = _division_segura(total_invertido, cantidad_comprada)
    costo_base_actual = cantidad_total * precio_promedio_compra
    ganancia_o_perdida = valor_actual_usd - costo_base_actual if costo_base_actual > 0 else utilidades_numericas.a_decimal(0)
    porcentaje_ganancia = _division_segura(ganancia_o_perdida, costo_base_actual) * Decimal("100")
    return {
        "ticker": ticker, "cantidad": cantidad_total, "precio_actual": precio_actual,
        "valor_usdt": valor_actual_usd, "precio_promedio_compra": precio_promedio_compra,
        "costo_base_actual": costo_base_actual, "ganancia_perdida": ganancia_o_perdida,
        "porcentaje_ganancia": porcentaje_ganancia,
    }

def _formatear_activo_para_presentacion(
    activo_calculado: Dict[str, Any],
    cripto_info: Dict[str, Any],
    saldos: Dict[str, Decimal],
    total_billetera_usd: Decimal,
) -> Dict[str, Any]:
    """Toma un activo con métricas calculadas y lo prepara para su presentación en la UI.

    Este es el paso final del pipeline para un activo individual. Convierte todos
    los valores `Decimal` a cadenas de texto con formato (ej. "$1,234.56"),
    añade metadatos útiles para la UI (nombre, logo, si es 'polvo'), y calcula
    el porcentaje que el activo representa en el portafolio total.

    Args:
        activo_calculado: Diccionario con las métricas pre-calculadas.
        cripto_info: Diccionario con información estática (nombre, logo).
        saldos: Diccionario con los saldos 'disponible' y 'reservado'.
        total_billetera_usd: Valor total del portafolio para calcular el %.

    Returns:
        Un diccionario final, listo para ser serializado a JSON.
    """
    porcentaje_en_billetera = _division_segura(activo_calculado["valor_usdt"], total_billetera_usd) * Decimal("100")
    es_polvo = activo_calculado["valor_usdt"] < config.UMBRAL_POLVO_USD

    cantidad_total = activo_calculado["cantidad"]
    saldo_disponible = saldos.get("disponible", utilidades_numericas.a_decimal(0))
    saldo_reservado = saldos.get("reservado", utilidades_numericas.a_decimal(0))

    return {
        "ticker": activo_calculado["ticker"],
        "nombre": cripto_info.get("nombre", activo_calculado["ticker"]),
        "logo": cripto_info.get("logo", ""),
        "es_polvo": es_polvo,
        
        "cantidad_total": str(cantidad_total),
        "cantidad_disponible": str(saldo_disponible),
        "cantidad_reservada": str(saldo_reservado),

        "cantidad_total_formatted": utilidades_numericas.formato_cantidad_cripto(cantidad_total),
        "cantidad_disponible_formatted": utilidades_numericas.formato_cantidad_cripto(saldo_disponible),
        "cantidad_reservada_formatted": utilidades_numericas.formato_cantidad_cripto(saldo_reservado),
        
        "precio_actual_formatted": utilidades_numericas.formato_cantidad_usd(activo_calculado["precio_actual"]),
        "valor_usdt_formatted": utilidades_numericas.formato_cantidad_usd(activo_calculado["valor_usdt"]),
        "ganancia_perdida_formatted": utilidades_numericas.formato_cantidad_usd(activo_calculado["ganancia_perdida"]),
        "ganancia_perdida_cruda": str(activo_calculado["ganancia_perdida"]),
        "porcentaje_ganancia_formatted": utilidades_numericas.formato_porcentaje(activo_calculado["porcentaje_ganancia"]),
        "porcentaje_formatted": utilidades_numericas.formato_porcentaje(porcentaje_en_billetera),
    }

def estado_actual_completo(
    ruta_billetera: str = config.BILLETERA_PATH,
    ruta_historial: str = config.HISTORIAL_PATH,
    ruta_cotizaciones: str = config.COTIZACIONES_PATH,
) -> List[Dict[str, Any]]:
    """Orquesta la creación del estado completo y formateado de la billetera."""
    billetera = cargar_billetera(ruta_archivo=ruta_billetera)
    historial = cargar_historial(ruta_archivo=ruta_historial)
    cotizaciones_raw = cargar_datos_cotizaciones(ruta_archivo=ruta_cotizaciones)
    
    # Crear un diccionario para búsqueda rápida de información y precios
    info_criptos = {c.get('ticker'): c for c in cotizaciones_raw if c.get('ticker')}
    precios_locales = {ticker: utilidades_numericas.a_decimal(info.get('precio_usd', '0')) for ticker, info in info_criptos.items()}
    
    # Forzar datos canónicos para USDT para asegurar consistencia
    info_criptos[config.MONEDA_FIAT_DEFAULT] = {
        'nombre': 'Tether', 
        'logo': 'https://assets.coingecko.com/coins/images/325/large/Tether.png?1696501661',
        'ticker': config.MONEDA_FIAT_DEFAULT
    }

    datos_compra_por_ticker = _preparar_datos_compra(historial)
    activos_calculados = []
    
    for ticker, activo_data in billetera.items():
        saldos = activo_data.get("saldos", {})
        cantidad_total = utilidades_numericas.a_decimal(saldos.get("disponible", 0)) + utilidades_numericas.a_decimal(saldos.get("reservado", 0))

        if cantidad_total >= config.UMBRAL_CASI_CERO:
            cripto_info_actual = info_criptos.get(ticker, {"nombre": ticker, "logo": ""})

            if ticker == config.MONEDA_FIAT_DEFAULT:
                metricas = {
                    "ticker": ticker, "cantidad": cantidad_total, "precio_actual": utilidades_numericas.a_decimal(1),
                    "valor_usdt": cantidad_total, "ganancia_perdida": utilidades_numericas.a_decimal(0),
                    "porcentaje_ganancia": utilidades_numericas.a_decimal(0),
                }
            else:
                precio_actual = precios_locales.get(ticker, utilidades_numericas.a_decimal(0))
                datos_compra_activo = datos_compra_por_ticker.get(ticker, {})
                metricas = _calcular_metricas_activo(ticker, cantidad_total, precio_actual, datos_compra_activo)
            
            metricas['cripto_info'] = cripto_info_actual
            metricas['saldos'] = saldos
            activos_calculados.append(metricas)

    activos_calculados.sort(key=lambda x: x["valor_usdt"], reverse=True)
    total_billetera_usd = sum(activo["valor_usdt"] for activo in activos_calculados)

    activos_para_presentacion = [
        _formatear_activo_para_presentacion(activo, activo["cripto_info"], activo["saldos"], total_billetera_usd)
        for activo in activos_calculados
    ]
    return activos_para_presentacion

def obtener_historial_formateado(
    ruta_historial: str = config.HISTORIAL_PATH,
) -> List[Dict[str, Any]]:
    """Carga y formatea el historial de transacciones para el frontend."""
    historial_crudo = cargar_historial(ruta_archivo=ruta_historial)
    historial_formateado = []

    for item in historial_crudo:
        tipo_op = item.get('tipo', '')
        origen = item.get('origen', {})
        destino = item.get('destino', {})
        par_origen = origen.get('ticker', '?')
        par_destino = destino.get('ticker', '?')
        
        # Lógica simplificada para determinar la cantidad principal de la operación
        if config.ACCION_COMPRAR in tipo_op.lower():
            cantidad = utilidades_numericas.a_decimal(destino.get('cantidad'))
        else: # Venta
            cantidad = utilidades_numericas.a_decimal(origen.get('cantidad'))

        item_formateado = {
            "id": item.get("id"),
            "tipo": tipo_op,
            "fecha_formatted": format_datetime(item.get('timestamp')),
            "par_formatted": f"{par_destino}/{par_origen}",
            "tipo_formatted": tipo_op.replace('-', ' ').capitalize(),
            "cantidad_formatted": utilidades_numericas.formato_cantidad_cripto(cantidad),
            "valor_total_formatted": utilidades_numericas.formato_cantidad_usd(utilidades_numericas.a_decimal(item.get('valor_usd'))),
        }
        historial_formateado.append(item_formateado)

    return historial_formateado


def obtener_comisiones_formateadas(
    ruta_comisiones: str = config.COMISIONES_PATH,
    ruta_cotizaciones: str = config.COTIZACIONES_PATH,
) -> List[Dict[str, Any]]:
    """
    Carga el historial de comisiones y lo enriquece con datos de presentación
    como logos y valores formateados.
    """
    comisiones_crudas = cargar_comisiones(ruta_archivo=ruta_comisiones)
    cotizaciones_crudas = cargar_datos_cotizaciones(ruta_archivo=ruta_cotizaciones)

    # Crear un diccionario para búsqueda rápida de logos para mayor eficiencia
    info_criptos = {c.get('ticker'): c for c in cotizaciones_crudas if c.get('ticker')}
    
    # Añadir info de USDT por si no viene en las cotizaciones
    if config.MONEDA_FIAT_DEFAULT not in info_criptos:
        info_criptos[config.MONEDA_FIAT_DEFAULT] = {
            'logo': 'https://assets.coingecko.com/coins/images/325/large/Tether.png?1696501661'
        }

    comisiones_formateadas = []
    for comision in comisiones_crudas:
        ticker = comision.get('ticker')
        cripto_info = info_criptos.get(ticker, {})

        item_formateado = {
            "id": comision.get("id"),
            "timestamp_formatted": format_datetime(comision.get('timestamp')),
            "ticker": ticker,
            "logo": cripto_info.get('logo', ''),  # Usar un string vacío como fallback seguro
            "cantidad_formatted": utilidades_numericas.formato_cantidad_cripto(utilidades_numericas.a_decimal(comision.get('cantidad'))),
            "valor_usd_formatted": utilidades_numericas.formato_cantidad_usd(utilidades_numericas.a_decimal(comision.get('valor_usd')))
        }
        comisiones_formateadas.append(item_formateado)
    
    return comisiones_formateadas