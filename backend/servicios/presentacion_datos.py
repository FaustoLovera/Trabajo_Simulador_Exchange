"""
Servicio de Presentación de Datos.

Este módulo se encarga de tomar los datos crudos de la aplicación (como las cotizaciones)
y enriquecerlos con formato y lógica de presentación para ser consumidos directamente
por el frontend.
"""

from decimal import Decimal
from backend.acceso_datos.datos_cotizaciones import cargar_datos_cotizaciones
from backend.utils.formatters import (
    formato_valor_monetario,
    formato_porcentaje,
    formato_numero_grande,
)


def _get_indicador_rendimiento(valor_str: str) -> dict:
    """
    Analiza un valor de rendimiento y devuelve un diccionario con la clase CSS y
    el símbolo de flecha correspondiente.

    Args:
        valor_str (str): El valor de rendimiento como string.

    Returns:
        dict: Un diccionario con las claves 'className' y 'arrow'.
    """
    try:
        valor = Decimal(valor_str)
        if valor >= 0:
            return {"className": "positivo", "arrow": "▲"}
        return {"className": "negativo", "arrow": "▼"}
    except (ValueError, TypeError):
        return {"className": "", "arrow": ""}


def obtener_cotizaciones_formateadas() -> list[dict]:
    """
    Carga las cotizaciones crudas y las transforma en una lista de diccionarios
    listos para ser renderizados en el frontend.

    Esta función añade campos formateados, indicadores de rendimiento y cualquier
    otra lógica de presentación necesaria.

    Returns:
        list[dict]: Una lista de diccionarios con los datos de cotización
                    enriquecidos para la presentación.
    """
    cotizaciones_crudas = cargar_datos_cotizaciones()
    cotizaciones_presentacion = []

    for cripto in cotizaciones_crudas:
        # Extraer los valores crudos para procesarlos
        ticker = cripto.get("ticker", "")
        precio_usd_crudo = cripto.get("precio_usd", "0")
        perf_1h_crudo = cripto.get("1h_%", "0")
        perf_24h_crudo = cripto.get("24h_%", "0")
        perf_7d_crudo = cripto.get("7d_%", "0")
        market_cap_crudo = cripto.get("market_cap", "0")
        volumen_24h_crudo = cripto.get("volumen_24h", "0")
        circulating_supply_crudo = cripto.get("circulating_supply", "0")

        # Ensamblar el nuevo diccionario de presentación
        cripto_presentacion = {
            # Datos básicos que no cambian
            "id": cripto.get("id"),
            "nombre": cripto.get("nombre"),
            "ticker": ticker,
            "logo": cripto.get("logo"),

            # Datos formateados usando los formatters
            "precio_usd_formatted": formato_valor_monetario(Decimal(precio_usd_crudo)),
            "market_cap_formatted": formato_numero_grande(Decimal(market_cap_crudo)),
            "volumen_24h_formatted": formato_numero_grande(Decimal(volumen_24h_crudo)),
            
            # Formateo especial para el supply circulante
            "circulating_supply_formatted": (
                f"{Decimal(circulating_supply_crudo):,.0f} {ticker}"
                if circulating_supply_crudo != "0"
                else "-"
            ),

            # Campos de rendimiento formateados
            "1h_formatted": formato_porcentaje(Decimal(perf_1h_crudo)),
            "24h_formatted": formato_porcentaje(Decimal(perf_24h_crudo)),
            "7d_formatted": formato_porcentaje(Decimal(perf_7d_crudo)),

            # Indicadores de rendimiento (clase CSS y flecha)
            "perf_1h": _get_indicador_rendimiento(perf_1h_crudo),
            "perf_24h": _get_indicador_rendimiento(perf_24h_crudo),
            "perf_7d": _get_indicador_rendimiento(perf_7d_crudo),
        }
        cotizaciones_presentacion.append(cripto_presentacion)

    return cotizaciones_presentacion