"""Módulo de Transformación para la Capa de Presentación (Presentation Layer).

Este módulo actúa como un adaptador entre los datos internos del backend y las
necesidades de la interfaz de usuario. Su única responsabilidad es tomar
estructuras de datos crudas y transformarlas en un formato enriquecido, con
campos pre-formateados y metadatos adicionales para facilitar su renderizado
en el frontend.

Este enfoque desacopla la lógica de negocio del formato de presentación,
permitiendo que cada uno evolucione de forma independiente.
"""

from typing import Any, Dict, List

from backend.acceso_datos.datos_cotizaciones import cargar_datos_cotizaciones
from backend.utils.formatters import get_performance_indicator
from backend.utils.utilidades_numericas import (
    a_decimal,
    formato_cantidad_usd,
    formato_numero_grande,
    formato_porcentaje,
)

def obtener_cotizaciones_formateadas() -> List[Dict[str, Any]]:
    """Carga, procesa y formatea los datos de cotizaciones para la UI.

    Esta función implementa un pipeline de transformación en tres pasos:
    1.  **Carga y Deserialización**: Carga los datos crudos y convierte todos los
        valores numéricos (almacenados como strings) a objetos `Decimal` para
        garantizar la precisión.
    2.  **Enriquecimiento y Formateo**: Crea un nuevo diccionario de presentación
        que contiene tanto los datos originales como nuevos campos con el sufijo
        `_formatted` (ej. "$1,234.56", "+5.2%").
    3.  **Añadir Indicadores**: Genera indicadores visuales (ej. 'positivo',
        'negativo') para facilitar el renderizado condicional en el frontend.

    Returns:
        Una lista de diccionarios, donde cada uno representa una criptomoneda
        con datos listos para ser mostrados en la interfaz de usuario.
    """
    cotizaciones_crudas = cargar_datos_cotizaciones()
    cotizaciones_presentacion = []

    for cripto in cotizaciones_crudas:
        # 1. Deserialización: Convertir strings a Decimal para poder operar.
        precio_usd = a_decimal(cripto.get("precio_usd"))
        perf_1h = a_decimal(cripto.get("1h_%"))
        perf_24h = a_decimal(cripto.get("24h_%"))
        perf_7d = a_decimal(cripto.get("7d_%"))
        market_cap = a_decimal(cripto.get("market_cap"))
        volumen_24h = a_decimal(cripto.get("volumen_24h"))
        circulating_supply = a_decimal(cripto.get("circulating_supply"))
        ticker = cripto.get("ticker", "")

        # 2. Enriquecimiento: Crear un nuevo diccionario con campos formateados.
        # Se mantienen los campos originales y se añaden nuevos con el sufijo `_formatted`
        # o `perf_` para ser usados directamente en la UI.

        cripto_presentacion = {
            "id": cripto.get("id"),
            "nombre": cripto.get("nombre"),
            "ticker": ticker,
            "logo": cripto.get("logo"),

            "precio_usd_formatted": formato_cantidad_usd(precio_usd),
            "market_cap_formatted": formato_numero_grande(market_cap),
            "volumen_24h_formatted": formato_numero_grande(volumen_24h),
            
            "circulating_supply_formatted": (
                f"{formato_numero_grande(circulating_supply)} {ticker}"
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