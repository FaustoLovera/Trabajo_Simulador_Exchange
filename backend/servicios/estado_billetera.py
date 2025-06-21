"""
Servicio para calcular y formatear el estado de la billetera y el historial.

Este módulo centraliza la lógica de negocio para procesar los datos crudos de la
billetera, el historial de transacciones y las cotizaciones. Genera una vista
completa y enriquecida con cálculos financieros (ganancias/pérdidas, precios
promedio) y campos formateados listos para ser consumidos por el frontend.
"""

from decimal import Decimal
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_historial import cargar_historial
from backend.acceso_datos.datos_cotizaciones import obtener_precio, cargar_datos_cotizaciones
from backend.utils.formatters import formato_valor_monetario, formato_cantidad_cripto, formato_porcentaje, formato_fecha_hora

def calcular_detalle_cripto(ticker: str, cantidad_actual: str | Decimal, precios: dict, historial: list[dict], info_cripto: dict) -> dict:
    """
    Calcula métricas financieras detalladas para una única criptomoneda en la billetera.

    Args:
        ticker (str): El ticker de la criptomoneda (ej. "BTC").
        cantidad_actual (str | Decimal): La cantidad de la criptomoneda en posesión.
        precios (dict): Un diccionario con los precios actuales de todas las criptos.
        historial (list[dict]): El historial completo de transacciones.
        info_cripto (dict): Un diccionario con información básica de la cripto (nombre, logo).

    Returns:
        dict: Un diccionario con los datos calculados, incluyendo valor actual,
              precio promedio de compra, inversión total y ganancias/pérdidas.
    """
    cantidad_actual = Decimal(str(cantidad_actual))
    precio_actual = precios.get(ticker, Decimal("0"))
    valor_usdt = cantidad_actual * precio_actual

    # Filtra solo las compras de la criptomoneda actual para calcular el costo base
    compras = [
        op for op in historial
        if op.get("tipo") == "compra" and op.get("destino", {}).get("ticker") == ticker
    ]

    cantidad_comprada = sum(Decimal(str(op.get("destino", {}).get("cantidad", "0"))) for op in compras)
    total_invertido = sum(Decimal(str(op.get("valor_usd", "0"))) for op in compras)

    # Función local para evitar división por cero
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

def estado_actual_completo() -> list[dict]:
    """
    Genera un estado completo y formateado de todos los activos en la billetera.

    Carga la billetera, el historial y las cotizaciones. Para cada activo, calcula
    sus métricas financieras, añade campos formateados para la UI y determina su
    peso porcentual en la billetera. Finalmente, convierte todos los valores
    Decimal a string para asegurar la serialización JSON.

    Returns:
        list[dict]: Una lista de diccionarios, cada uno representando un activo
                    con todos sus datos brutos, calculados y formateados.
    """
    billetera = cargar_billetera()
    historial = cargar_historial()
    todas_las_cotizaciones = cargar_datos_cotizaciones()
    info_map = {c.get('ticker'): c for c in todas_las_cotizaciones}
    precios = {ticker: obtener_precio(ticker) or Decimal("0") for ticker in billetera.keys()}

    detalles = []
    for ticker, cantidad in billetera.items():
        # USDT es un caso especial ya que no viene de la API de Coingecko
        if ticker == "USDT":
            info_cripto = {'nombre': 'Tether', 'ticker': 'USDT'}
        else:
            info_cripto = info_map.get(ticker, {'nombre': ticker})  # Fallback si no se encuentra

        detalle_calculado = calcular_detalle_cripto(ticker, cantidad, precios, historial, info_cripto)
        detalles.append(detalle_calculado)

    total_usdt = sum(d.get("valor_usdt", Decimal("0")) for d in detalles)
    division_por_cero_segura = lambda num, den: num / den if den != 0 else Decimal("0")

    # Segunda pasada para calcular porcentajes y añadir formato
    for detalle in detalles:
        porcentaje_billetera = division_por_cero_segura(detalle.get("valor_usdt", Decimal("0")), total_usdt) * Decimal("100")
        
        detalle["porcentaje"] = porcentaje_billetera
        detalle["es_polvo"] = detalle.get("valor_usdt", Decimal("0")) < Decimal("0.001")
        
        # Formateo condicional para USDT vs otras criptos
        if detalle["ticker"] == 'USDT':
            detalle["cantidad_formatted"] = formato_valor_monetario(detalle["cantidad"], simbolo="")
        else:
            detalle["cantidad_formatted"] = formato_cantidad_cripto(detalle["cantidad"])
        
        detalle["precio_actual_formatted"] = formato_valor_monetario(detalle.get("precio_actual", Decimal("0")), decimales=4)
        detalle["valor_usdt_formatted"] = formato_valor_monetario(detalle.get("valor_usdt", Decimal("0")))
        detalle["ganancia_perdida_formatted"] = formato_valor_monetario(detalle.get("ganancia_perdida", Decimal("0")))
        detalle["porcentaje_ganancia_formatted"] = formato_porcentaje(detalle.get("porcentaje_ganancia", Decimal("0")))
        detalle["porcentaje_formatted"] = formato_porcentaje(porcentaje_billetera)

        # Asegura que todos los valores Decimal se conviertan a string
        for k, v in detalle.items():
            if isinstance(v, Decimal):
                detalle[k] = str(v)
    
    return detalles

def obtener_historial_formateado() -> list[dict]:
    """
    Carga y formatea el historial de transacciones para su visualización.

    Para cada transacción, añade campos formateados como la fecha, el par de
    monedas, y los valores monetarios, listos para ser mostrados en la UI.

    Returns:
        list[dict]: Una lista de transacciones, cada una como un diccionario
                    enriquecido con datos formateados.
    """
    historial = cargar_historial()
    historial_formateado = []

    for item in historial:
        item_formateado = item.copy()

        if item.get('tipo') == 'compra':
            cantidad = Decimal(str(item.get('destino', {}).get('cantidad', '0')))
            par = f"{item.get('destino', {}).get('ticker', '?')}/{item.get('origen', {}).get('ticker', '?')}"
        else:  # Venta
            cantidad = Decimal(str(item.get('origen', {}).get('cantidad', '0')))
            par = f"{item.get('origen', {}).get('ticker', '?')}/{item.get('destino', {}).get('ticker', '?')}"

        # Añade campos formateados para la UI
        item_formateado['fecha_formatted'] = formato_fecha_hora(item.get('timestamp'))
        item_formateado['par_formatted'] = par
        item_formateado['tipo_formatted'] = item.get('tipo', '').capitalize()
        item_formateado['cantidad_formatted'] = formato_cantidad_cripto(cantidad)
        item_formateado['valor_total_formatted'] = formato_valor_monetario(Decimal(str(item.get('valor_usd', '0'))))

        # Convierte todos los Decimal a string para serialización JSON segura
        for k, v in item_formateado.items():
            if isinstance(v, Decimal):
                item_formateado[k] = str(v)
            elif isinstance(v, dict):
                # Procesa diccionarios anidados también (ej. 'origen', 'destino')
                v_copy = v.copy()
                for sub_k, sub_v in v_copy.items():
                    if isinstance(sub_v, Decimal):
                        v_copy[sub_k] = str(sub_v)
                item_formateado[k] = v_copy

        historial_formateado.append(item_formateado)

    return historial_formateado