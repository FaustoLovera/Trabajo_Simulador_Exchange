# backend/servicios/trading_models.py
from flask import json
from .velas_logica import cargar_datos_cotizaciones
from ..acceso_datos.datos_billetera import cargar_billetera
from ..acceso_datos.datos_historial import cargar_historial
from .api_cotizaciones import obtener_velas_binance


def preparar_vista_trading():
    """
    Orquesta la carga y preparación de todos los datos necesarios para la vista de trading.
    """
    # 1. Carga de datos crudos
    obtener_velas_binance()
    criptos_disponibles = cargar_datos_cotizaciones()
    billetera = cargar_billetera()
    historial_crudo = cargar_historial()

    # 2. Pre-procesamos el historial en Python para añadir fecha y hora formateadas
    historial_formateado = []
    for item in historial_crudo:
        timestamp_str = item.get("timestamp")
        if timestamp_str and "T" in timestamp_str:
            # Separamos la cadena en fecha y hora
            partes = timestamp_str.split("T")
            fecha = partes[0]
            hora = partes[1].split(".")[0]  # Quitamos los microsegundos

            # Añadimos las nuevas claves al diccionario de la transacción
            item["fecha_formateada"] = fecha
            item["hora_formateada"] = hora
        else:
            # Si el timestamp no existe o tiene un formato inesperado
            item["fecha_formateada"] = "Fecha N/A"
            item["hora_formateada"] = ""

        historial_formateado.append(item)

    # 3. Transformación de datos para la vista
    monedas_propias = {
        ticker: saldo for ticker, saldo in billetera.items() if saldo > 0
    }

    lista_todas_criptos_js = [
        {"ticker": c.get("ticker", "").upper(), "nombre": c.get("nombre", "N/A")}
        for c in criptos_disponibles
    ]
    lista_monedas_propias_js = [
        {"ticker": ticker, "nombre": ticker} for ticker in monedas_propias.keys()
    ]

    # 4. Devolvemos el contexto completo, usando el historial ya procesado
    return {
        "criptos": criptos_disponibles,
        "monedas_propias": monedas_propias,
        "historial": historial_formateado,  # <-- ¡Usamos la nueva lista!
        "lista_todas_las_criptos_json": json.dumps(lista_todas_criptos_js),
        "lista_monedas_propias_json": json.dumps(lista_monedas_propias_js),
    }
