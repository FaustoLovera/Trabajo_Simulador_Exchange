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
    """
    datos_compra_por_ticker = {}
    for operacion in historial:
        # Solo consideramos las compras para el cálculo de P&L
        if operacion.get("tipo") == "compra" or (isinstance(operacion.get("tipo"), str) and operacion.get("tipo").endswith("-compra")):
            destino = operacion.get("destino", {})
            ticker = destino.get("ticker")
            if not ticker:
                continue

            if ticker not in datos_compra_por_ticker:
                datos_compra_por_ticker[ticker] = {
                    "total_invertido": Decimal("0"),
                    "cantidad_comprada": Decimal("0"),
                }
            
            datos_compra_por_ticker[ticker]["total_invertido"] += Decimal(str(operacion.get("valor_usd", "0")))
            datos_compra_por_ticker[ticker]["cantidad_comprada"] += Decimal(str(destino.get("cantidad", "0")))
            
    return datos_compra_por_ticker


def _calcular_metricas_activo(ticker: str, cantidad_total: Decimal, precio_actual: Decimal, datos_compra: dict) -> dict:
    """
    Calcula las métricas financieras clave (sin formato) para un único activo.
    """
    valor_actual_usd = cantidad_total * precio_actual

    total_invertido = datos_compra.get("total_invertido", Decimal("0"))
    cantidad_comprada = datos_compra.get("cantidad_comprada", Decimal("0"))

    precio_promedio_compra = _division_segura(total_invertido, cantidad_comprada)
    costo_base_actual = cantidad_total * precio_promedio_compra
    ganancia_o_perdida = valor_actual_usd - costo_base_actual if costo_base_actual > 0 else Decimal("0")
    porcentaje_ganancia = _division_segura(ganancia_o_perdida, costo_base_actual) * Decimal("100")

    return {
        "ticker": ticker,
        "cantidad": cantidad_total,
        "precio_actual": precio_actual,
        "valor_usdt": valor_actual_usd,
        "precio_promedio_compra": precio_promedio_compra,
        "costo_base_actual": costo_base_actual,
        "ganancia_perdida": ganancia_o_perdida,
        "porcentaje_ganancia": porcentaje_ganancia,
    }

def _formatear_activo_para_presentacion(activo_calculado: dict, saldos: dict, total_billetera_usd: Decimal, info_cripto: dict) -> dict:
    """
    Toma un activo con métricas calculadas y le añade todos los campos formateados.
    """
    porcentaje_en_billetera = _division_segura(activo_calculado["valor_usdt"], total_billetera_usd) * Decimal("100")

    if activo_calculado["ticker"] == 'USDT':
        cantidad_formateada = formato_valor_monetario(activo_calculado["cantidad"], simbolo="")
    else:
        cantidad_formateada = formato_cantidad_cripto(activo_calculado["cantidad"])

    return {
        "ticker": activo_calculado["ticker"],
        "nombre": info_cripto.get("nombre", activo_calculado["ticker"]),
        "es_polvo": activo_calculado["valor_usdt"] < Decimal("0.01"),
        
        # Cantidades
        "cantidad": str(activo_calculado["cantidad"]),
        "cantidad_formatted": cantidad_formateada,
        "cantidad_disponible": str(saldos.get("disponible", "0")),
        "cantidad_reservada": str(saldos.get("reservado", "0")),

        # Valores monetarios
        "precio_actual_formatted": formato_valor_monetario(activo_calculado["precio_actual"], decimales=4),
        "valor_usdt_formatted": formato_valor_monetario(activo_calculado["valor_usdt"]),
        "ganancia_perdida": str(activo_calculado["ganancia_perdida"]),
        "ganancia_perdida_formatted": formato_valor_monetario(activo_calculado["ganancia_perdida"]),
        
        # Porcentajes
        "porcentaje_ganancia_formatted": formato_porcentaje(activo_calculado["porcentaje_ganancia"]),
        "porcentaje_formatted": formato_porcentaje(porcentaje_en_billetera),
    }

# --- Función Principal de la Billetera (CORREGIDA) ---

def estado_actual_completo() -> list[dict]:
    """
    Genera un estado completo y formateado de todos los activos en la billetera,
    manejando la nueva estructura con saldos disponibles y reservados.
    """
    billetera = cargar_billetera()
    historial = cargar_historial()
    todas_las_cotizaciones = cargar_datos_cotizaciones()
    
    info_cripto_map = {c.get('ticker'): c for c in todas_las_cotizaciones}
    datos_compra_por_ticker = _preparar_datos_compra(historial)

    activos_calculados = []
    # === INICIO DE LA CORRECCIÓN ===
    for ticker, saldos in billetera.items():
        # 1. Extraer saldos de la nueva estructura
        saldo_disponible = saldos.get("disponible", Decimal("0"))
        saldo_reservado = saldos.get("reservado", Decimal("0"))
        cantidad_total = saldo_disponible + saldo_reservado

        # 2. Comparar la CANTIDAD TOTAL, no el diccionario
        if cantidad_total <= Decimal("1e-8"):
            continue
            
        precio_actual = obtener_precio(ticker) or Decimal("0")
        datos_compra_activo = datos_compra_por_ticker.get(ticker, {})

        # 3. Calcular métricas usando la CANTIDAD TOTAL
        metricas = _calcular_metricas_activo(
            ticker,
            cantidad_total,
            precio_actual,
            datos_compra_activo
        )
        # Guardamos los saldos para el formateador
        metricas['saldos'] = saldos
        activos_calculados.append(metricas)
    # === FIN DE LA CORRECCIÓN ===

    total_billetera_usd = sum(activo["valor_usdt"] for activo in activos_calculados)

    activos_para_presentacion = []
    for activo in activos_calculados:
        ticker = activo["ticker"]
        info_cripto = info_cripto_map.get(ticker, {'nombre': ticker}) if ticker != "USDT" else {'nombre': 'Tether'}
        
        activo_formateado = _formatear_activo_para_presentacion(activo, activo['saldos'], total_billetera_usd, info_cripto)
        activos_para_presentacion.append(activo_formateado)

    return activos_para_presentacion

# --- Función para el Historial ---

def obtener_historial_formateado() -> list[dict]:
    """
    Carga y formatea el historial de transacciones para su visualización.
    """
    historial_crudo = cargar_historial()
    historial_formateado = []

    for item in historial_crudo:
        tipo_op = item.get('tipo', '')
        # Determinar el par y la cantidad principal de la operación
        if tipo_op.endswith('compra'):
            par_origen = item.get('origen', {}).get('ticker', '?')
            par_destino = item.get('destino', {}).get('ticker', '?')
            cantidad = Decimal(str(item.get('destino', {}).get('cantidad', '0')))
        else:  # Venta o Intercambio
            par_origen = item.get('origen', {}).get('ticker', '?')
            par_destino = item.get('destino', {}).get('ticker', '?')
            cantidad = Decimal(str(item.get('origen', {}).get('cantidad', '0')))

        item_formateado = {
            "id": item.get("id"),
            "tipo": tipo_op,
            "fecha_formatted": formato_fecha_hora(item.get('timestamp')),
            "par_formatted": f"{par_destino}/{par_origen}",
            "tipo_formatted": tipo_op.replace('-', ' ').capitalize(),
            "cantidad_formatted": formato_cantidad_cripto(cantidad),
            "valor_total_formatted": formato_valor_monetario(Decimal(str(item.get('valor_usd', '0')))),
        }
        historial_formateado.append(item_formateado)

    return historial_formateado