from flask import render_template
from decimal import Decimal
from backend.acceso_datos.datos_billetera import cargar_billetera
from backend.acceso_datos.datos_historial import cargar_historial
from backend.acceso_datos.datos_cotizaciones import obtener_precio


# En backend/servicios/estado_billetera.py

def calcular_detalle_cripto(ticker, cantidad_actual, precios, historial):
    """
    Calcula el estado financiero de una criptomoneda en base a su cantidad actual, el precio de mercado
    y el historial de compras.
    """
    cantidad_actual = Decimal(str(cantidad_actual))
    precio_actual = precios.get(ticker, Decimal('0')).quantize(Decimal('0.000001'))
    valor_usdt = (cantidad_actual * precio_actual).quantize(Decimal('0.01'))

    # Filtra las operaciones de compra donde el 'ticker' que estamos analizando fue el DESTINO.
    compras = [
        op for op in historial 
        if op.get("tipo") == "compra" and op.get("destino", {}).get("ticker") == ticker
    ]

    # Usamos .get() para evitar errores si alguna operación antigua no tiene el formato nuevo.
    cantidad_comprada = sum(Decimal(str(op.get("destino", {}).get("cantidad", "0"))) for op in compras)
    total_invertido = sum(Decimal(str(op.get("valor_usd", "0"))) for op in compras)
    
    # El resto de la función no necesita cambios...
    division_por_0_segura = lambda num, den: num / den if den != 0 else Decimal('0')

    precio_promedio = division_por_0_segura(total_invertido, cantidad_comprada).quantize(Decimal('0.000001')) if cantidad_comprada else Decimal('0')
    invertido_actual = (cantidad_actual * precio_promedio).quantize(Decimal('0.01'))

    ganancia = (valor_usdt - invertido_actual).quantize(Decimal('0.01'))
    porcentaje_ganancia = division_por_0_segura(ganancia, invertido_actual) * Decimal('100') if invertido_actual != 0 else Decimal('0')

    return {
        "ticker": ticker,
        "cantidad": cantidad_actual,
        "valor_usdt": valor_usdt,
        "precio_actual": precio_actual,
        "precio_promedio": precio_promedio,
        "invertido": invertido_actual,
        "ganancia_perdida": ganancia,
        "porcentaje_ganancia": porcentaje_ganancia,
    }


def estado_actual_completo():
    """
    Calcula un resumen financiero completo del portafolio de criptomonedas actual.

    Este resumen incluye, para cada activo con saldo significativo (> 0.000001):
    - Cantidad disponible
    - Valor de mercado en USDT
    - Precio promedio de compra
    - Monto invertido
    - Ganancia/pérdida neta y en porcentaje
    - Porcentaje de participación en el portafolio total

    Returns:
        List[Dict]: Lista de diccionarios, cada uno representando una criptomoneda con su detalle financiero.
    """

    # Cargar los datos actuales desde archivos locales
    billetera = {k: Decimal(str(v)) for k, v in cargar_billetera().items()}
    if "USDT" in billetera:
        billetera["USDT"] = billetera["USDT"].quantize(Decimal("0.01"))
    
    # Obtener precios para cada cripto en la billetera
    precios = {ticker: obtener_precio(ticker) or Decimal('0') for ticker in billetera.keys()}
    historial = cargar_historial()

    billetera_filtrada = billetera

    # Calcular el detalle financiero de cada criptomoneda
    detalles = list(
        map(
            lambda par: calcular_detalle_cripto(par[0], par[1], precios, historial),
            billetera_filtrada.items(),
        )
    )

    # Calcular el valor total en USDT del portafolio
    total_usdt = sum(Decimal(str(d["valor_usdt"])) for d in detalles)

    # Función para calcular el porcentaje que representa cada cripto sobre el total
    calcular_porcentaje = lambda valor_usdt: ((Decimal(str(valor_usdt)) / total_usdt) * Decimal('100')).quantize(Decimal('0.01')) if total_usdt > 0 else Decimal('0')

    # Asignar el porcentaje correspondiente a cada criptomoneda y los colores
    for detalle_cripto in detalles:
        detalle_cripto["porcentaje"] = calcular_porcentaje(detalle_cripto["valor_usdt"])
        detalle_cripto["color_ganancia"] = "green" if detalle_cripto["ganancia_perdida"] >= 0 else "red"
        detalle_cripto["color_porcentaje"] = "green" if detalle_cripto["porcentaje_ganancia"] >= 0 else "red"
        detalle_cripto["es_polvo"] = detalle_cripto["valor_usdt"] < Decimal("0.001")
        # Truncamiento a 8 decimales eliminado, se mantiene la cantidad tal cual
        detalle_cripto["cantidad"] = detalle_cripto["cantidad"]

    return detalles
