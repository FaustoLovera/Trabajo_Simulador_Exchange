"""
Servicio de Presentación de Datos.

Este módulo se encarga de tomar los datos crudos de la aplicación (como las cotizaciones)
y enriquecerlos con formato y lógica de presentación para ser consumidos directamente
por el frontend. Utiliza el módulo `utilidades_numericas` para todo el formateo numérico.
"""

from backend.acceso_datos.datos_cotizaciones import cargar_datos_cotizaciones
from backend.utils.formatters import get_performance_indicator
from backend.utils.utilidades_numericas import (
    formato_cantidad_usd,
    formato_porcentaje,
    formato_numero_grande,
    a_decimal
)

def obtener_cotizaciones_formateadas() -> list[dict]:
    """
    Carga las cotizaciones crudas y las transforma en una lista de diccionarios
    listos para ser renderizados en el frontend.
    """
    cotizaciones_crudas = cargar_datos_cotizaciones()
    cotizaciones_presentacion = []

    for cripto in cotizaciones_crudas:
        precio_usd = a_decimal(cripto.get("precio_usd"))
        perf_1h = a_decimal(cripto.get("1h_%"))
        perf_24h = a_decimal(cripto.get("24h_%"))
        perf_7d = a_decimal(cripto.get("7d_%"))
        market_cap = a_decimal(cripto.get("market_cap"))
        volumen_24h = a_decimal(cripto.get("volumen_24h"))
        circulating_supply = a_decimal(cripto.get("circulating_supply"))
        ticker = cripto.get("ticker", "")

        cripto_presentacion = {
            "id": cripto.get("id"),
            "nombre": cripto.get("nombre"),
            "ticker": ticker,
            "logo": cripto.get("logo"),

            "precio_usd_formatted": formato_cantidad_usd(precio_usd),
            "market_cap_formatted": formato_numero_grande(market_cap),
            "volumen_24h_formatted": formato_numero_grande(volumen_24h),
            
            "circulating_supply_formatted": (
                f"{circulating_supply:,.0f} {ticker}"
                if circulating_supply > 0
                else "-"
            ),

            "1h_formatted": formato_porcentaje(perf_1h),
            "24h_formatted": formato_porcentaje(perf_24h),
            "7d_formatted": formato_porcentaje(perf_7d),

            "perf_1h": get_performance_indicator(perf_1h),
            "perf_24h": get_performance_indicator(perf_24h),
            "perf_7d": get_performance_indicator(perf_7d),
        }
        cotizaciones_presentacion.append(cripto_presentacion)

    return cotizaciones_presentacion