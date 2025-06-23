"""
Servicio para calcular y formatear el estado de la billetera y el historial.

Este módulo centraliza la lógica de negocio para procesar los datos crudos de la
billetera, el historial de transacciones y las cotizaciones. Genera una vista
completa y enriquecida con cálculos financieros (ganancias/pérdidas, precios
promedio) y campos formateados listos para ser consumidos por el frontend.

La reescritura se enfoca en la claridad, separando la lógica en funciones más
pequeñas y con responsabilidades únicas.
"""

from decimal import Decimal
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_historial import cargar_historial
from backend.acceso_datos.datos_cotizaciones import obtener_precio, cargar_datos_cotizaciones
from backend.utils.formatters import formato_valor_monetario, formato_cantidad_cripto, formato_porcentaje, formato_fecha_hora


# --- Funciones Auxiliares para el Cálculo de la Billetera ---
def _division_segura(numerador: Decimal, denominador: Decimal) -> Decimal:
    """Evita errores de división por cero devolviendo Decimal('0') si el denominador es cero."""
    if denominador == Decimal("0"):
        return Decimal("0")
    else:
        return numerador / denominador


def _preparar_datos_compra(historial: list[dict]) -> dict[str, dict]:
    """
    Procesa el historial de transacciones UNA SOLA VEZ para agregar los costos
    y cantidades de compra por cada criptomoneda.

    Esto es mucho más eficiente que filtrar el historial para cada moneda individualmente.

    Args:
        historial (list[dict]): El historial completo de transacciones.

    Returns:
        dict[str, dict]: Un diccionario donde la clave es el ticker de la criptomoneda
                         y el valor es otro diccionario con 'total_invertido' y
                         'cantidad_comprada'.
                         Ej: {'BTC': {'total_invertido': 5000, 'cantidad_comprada': 0.1}}
    """
    datos_compra_por_ticker = {}
    for operacion in historial:
        if operacion.get("tipo") == "compra":
            destino = operacion.get("destino", {})
            ticker = destino.get("ticker")
            if not ticker:
                continue

            # Inicializa el diccionario para el ticker si es la primera vez que lo vemos
            if ticker not in datos_compra_por_ticker:
                datos_compra_por_ticker[ticker] = {
                    "total_invertido": Decimal("0"),
                    "cantidad_comprada": Decimal("0"),
                }
            
            # Agrega los valores de la transacción actual
            datos_compra_por_ticker[ticker]["total_invertido"] += Decimal(str(operacion.get("valor_usd", "0")))
            datos_compra_por_ticker[ticker]["cantidad_comprada"] += Decimal(str(destino.get("cantidad", "0")))
            
    return datos_compra_por_ticker


def _calcular_metricas_activo(ticker: str, cantidad_actual: Decimal, precio_actual: Decimal, datos_compra: dict) -> dict:
    """
    Calcula las métricas financieras clave (sin formato) para un único activo.
    Esta función se enfoca puramente en los cálculos matemáticos.

    Args:
        ticker (str): El ticker del activo (ej. "BTC").
        cantidad_actual (Decimal): La cantidad del activo en la billetera.
        precio_actual (Decimal): El precio de mercado actual del activo.
        datos_compra (dict): La información de compra pre-procesada para este activo.

    Returns:
        dict: Un diccionario con las métricas calculadas (valor, P&L, etc.) como objetos Decimal.
    """
    valor_actual_usd = cantidad_actual * precio_actual

    # Obtiene los datos de compra para este activo específico
    total_invertido = datos_compra.get("total_invertido", Decimal("0"))
    cantidad_comprada = datos_compra.get("cantidad_comprada", Decimal("0"))

    # Calcula las métricas
    precio_promedio_compra = _division_segura(total_invertido, cantidad_comprada)
    costo_base_actual = cantidad_actual * precio_promedio_compra
    ganancia_o_perdida = valor_actual_usd - costo_base_actual
    porcentaje_ganancia = _division_segura(ganancia_o_perdida, costo_base_actual) * Decimal("100")

    return {
        "ticker": ticker,
        "cantidad": cantidad_actual,
        "precio_actual": precio_actual,
        "valor_usdt": valor_actual_usd,
        "precio_promedio_compra": precio_promedio_compra,
        "costo_base_actual": costo_base_actual,
        "ganancia_perdida": ganancia_o_perdida,
        "porcentaje_ganancia": porcentaje_ganancia,
    }


def _formatear_activo_para_presentacion(activo_calculado: dict, total_billetera_usd: Decimal, info_cripto: dict) -> dict:
    """
    Toma un activo con métricas calculadas y le añade todos los campos formateados
    para ser mostrados en la interfaz de usuario.

    Args:
        activo_calculado (dict): Un diccionario con las métricas del activo (valores Decimal).
        total_billetera_usd (Decimal): El valor total de toda la billetera en USD.
        info_cripto (dict): Un diccionario con información estática de la cripto (nombre, logo).

    Returns:
        dict: Un diccionario final listo para ser enviado como JSON, con todos los valores como strings.
    """
    porcentaje_en_billetera = _division_segura(activo_calculado["valor_usdt"], total_billetera_usd) * Decimal("100")

    # Formato condicional para la cantidad (USDT vs otras criptos)
    if activo_calculado["ticker"] == 'USDT':
        cantidad_formateada = formato_valor_monetario(activo_calculado["cantidad"], simbolo="")
    else:
        cantidad_formateada = formato_cantidad_cripto(activo_calculado["cantidad"])

    return {
        "ticker": activo_calculado["ticker"],
        "nombre": info_cripto.get("nombre", activo_calculado["ticker"]),
        "es_polvo": activo_calculado["valor_usdt"] < Decimal("0.01"),
        
        # === INICIO DE LA CORRECCIÓN ===
        # Devolvemos tanto el valor crudo (para la lógica del JS) como el formateado (para la vista).
        "cantidad": str(activo_calculado["cantidad"]),
        "cantidad_formatted": cantidad_formateada,
        # === FIN DE LA CORRECCIÓN ===

        "precio_actual_formatted": formato_valor_monetario(activo_calculado["precio_actual"], decimales=4),
        "valor_usdt_formatted": formato_valor_monetario(activo_calculado["valor_usdt"]),
        "ganancia_perdida_formatted": formato_valor_monetario(activo_calculado["ganancia_perdida"]),
        "porcentaje_ganancia_formatted": formato_porcentaje(activo_calculado["porcentaje_ganancia"]),
        "porcentaje_formatted": formato_porcentaje(porcentaje_en_billetera),

        # Incluir el valor crudo de ganancia/pérdida para lógica de color en el frontend
        "ganancia_perdida": str(activo_calculado["ganancia_perdida"]),
    }

# --- Función Principal de la Billetera ---

def estado_actual_completo() -> list[dict]:
    """
    Genera un estado completo y formateado de todos los activos en la billetera.
    El proceso está dividido en pasos claros para mejorar la legibilidad.
    """
    # PASO 1: Cargar todos los datos crudos necesarios
    billetera = cargar_billetera()
    historial = cargar_historial()
    todas_las_cotizaciones = cargar_datos_cotizaciones()
    
    # Crear mapas para acceso rápido a la información
    info_cripto_map = {c.get('ticker'): c for c in todas_las_cotizaciones}
    precios_actuales = {ticker: obtener_precio(ticker) or Decimal("0") for ticker in billetera.keys()}

    # PASO 2: Pre-procesar el historial para optimizar los cálculos
    datos_compra_por_ticker = _preparar_datos_compra(historial)

    # PASO 3: Calcular las métricas financieras para cada activo en la billetera
    activos_calculados = []
    for ticker, cantidad in billetera.items():
        if cantidad <= Decimal("1e-8"):  # Ignorar saldos de polvo insignificantes
            continue
            
        datos_compra_activo = datos_compra_por_ticker.get(ticker, {})
        metricas = _calcular_metricas_activo(
            ticker,
            cantidad,
            precios_actuales.get(ticker, Decimal("0")),
            datos_compra_activo
        )
        activos_calculados.append(metricas)

    # PASO 4: Calcular el valor total de la billetera
    total_billetera_usd = sum(activo["valor_usdt"] for activo in activos_calculados)

    # PASO 5: Formatear cada activo para la presentación final
    activos_para_presentacion = []
    for activo in activos_calculados:
        ticker = activo["ticker"]
        # Asignar información básica (nombre, logo)
        if ticker == "USDT":
            info_cripto = {'nombre': 'Tether'}
        else:
            info_cripto = info_cripto_map.get(ticker, {'nombre': ticker})
        
        activo_formateado = _formatear_activo_para_presentacion(activo, total_billetera_usd, info_cripto)
        activos_para_presentacion.append(activo_formateado)

    return activos_para_presentacion

# --- Función para el Historial ---

def obtener_historial_formateado() -> list[dict]:
    """
    Carga y formatea el historial de transacciones para su visualización.
    La lógica de formato está contenida para mayor claridad.
    """
    historial_crudo = cargar_historial()
    historial_formateado = []

    for item in historial_crudo:
        # Determinar el par y la cantidad principal de la operación
        if item.get('tipo') == 'compra':
            par_origen = item.get('origen', {}).get('ticker', '?')
            par_destino = item.get('destino', {}).get('ticker', '?')
            cantidad = Decimal(str(item.get('destino', {}).get('cantidad', '0')))
        else:  # Venta o Intercambio
            par_origen = item.get('origen', {}).get('ticker', '?')
            par_destino = item.get('destino', {}).get('ticker', '?')
            cantidad = Decimal(str(item.get('origen', {}).get('cantidad', '0')))

        # Ensamblar el diccionario final con campos formateados
        item_formateado = {
            "id": item.get("id"),
            "tipo": item.get("tipo"),
            "fecha_formatted": formato_fecha_hora(item.get('timestamp')),
            "par_formatted": f"{par_destino}/{par_origen}",
            "tipo_formatted": item.get('tipo', '').capitalize(),
            "cantidad_formatted": formato_cantidad_cripto(cantidad),
            "valor_total_formatted": formato_valor_monetario(Decimal(str(item.get('valor_usd', '0')))),
        }
        historial_formateado.append(item_formateado)

    return historial_formateado