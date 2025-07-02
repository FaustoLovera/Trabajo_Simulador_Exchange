import pytest
import json
from decimal import Decimal

# Importamos las funciones a probar, ahora refactorizadas
from backend.servicios.estado_billetera import (
    _calcular_metricas_activo,
    _preparar_datos_compra,
    estado_actual_completo,
    obtener_historial_formateado
)

# --- Fixtures: Datos de prueba reutilizables ---

@pytest.fixture
def datos_compra_btc():
    """Fixture que proporciona datos de compra para Bitcoin."""
    return {
        "total_invertido": Decimal("45000"),
        "cantidad_comprada": Decimal("1.5")
    }

# --- Tests para las funciones puras (sin cambios, no dependen de I/O) ---

def test_preparar_datos_compra_mixto():
    """
    Prueba que solo se suman compras (ignora ventas y USDT) y agrupa por ticker.
    """
    historial = [
        {"tipo": "compra", "destino": {"ticker": "BTC", "cantidad": "1.0"}, "valor_usd": "30000"},
        {"tipo": "venta", "destino": {"ticker": "BTC", "cantidad": "0.5"}, "valor_usd": "15000"},
        {"tipo": "compra", "destino": {"ticker": "ETH", "cantidad": "2.0"}, "valor_usd": "20000"},
        {"tipo": "compra", "destino": {"ticker": "USDT", "cantidad": "1000"}, "valor_usd": "1000"},
    ]
    resultado = _preparar_datos_compra(historial)
    assert set(resultado.keys()) == {"BTC", "ETH"}
    assert resultado["BTC"]["total_invertido"] == Decimal("30000")
    assert resultado["BTC"]["cantidad_comprada"] == Decimal("1.0")
    assert resultado["ETH"]["total_invertido"] == Decimal("20000")
    assert resultado["ETH"]["cantidad_comprada"] == Decimal("2.0")

def test_preparar_datos_compra_vacio():
    """
    Prueba que un historial vacío retorna un diccionario vacío.
    """
    resultado = _preparar_datos_compra([])
    assert resultado == {}

def test_preparar_datos_compra_sin_compras():
    """
    Prueba que un historial sin compras retorna un diccionario vacío.
    """
    historial = [
        {"tipo": "venta", "destino": {"ticker": "BTC", "cantidad": "1.0"}, "valor_usd": "30000"},
        {"tipo": "transferencia", "destino": {"ticker": "ETH", "cantidad": "2.0"}, "valor_usd": "20000"},
    ]
    resultado = _preparar_datos_compra(historial)
    assert resultado == {}

def test_preparar_datos_compra_agrupa_multiples_compras():
    """
    Prueba que agrupa correctamente múltiples compras del mismo activo.
    """
    historial = [
        {"tipo": "compra", "destino": {"ticker": "BTC", "cantidad": "1.0"}, "valor_usd": "30000"},
        {"tipo": "compra", "destino": {"ticker": "BTC", "cantidad": "0.5"}, "valor_usd": "15000"},
        {"tipo": "compra", "destino": {"ticker": "BTC", "cantidad": "0.25"}, "valor_usd": "7000"},
    ]
    resultado = _preparar_datos_compra(historial)
    assert set(resultado.keys()) == {"BTC"}
    assert resultado["BTC"]["total_invertido"] == Decimal("52000")
    assert resultado["BTC"]["cantidad_comprada"] == Decimal("1.75")


def test_calcular_metricas_activo(datos_compra_btc):
    """Prueba la función de cálculo de métricas para un activo."""
    ticker = "BTC"
    cantidad_actual = Decimal("1.5")
    precio_actual = Decimal("40000")
    
    resultado = _calcular_metricas_activo(ticker, cantidad_actual, precio_actual, datos_compra_btc)

    assert resultado["ticker"] == "BTC"
    assert resultado["cantidad"] == cantidad_actual
    assert resultado["precio_actual"] == precio_actual
    assert resultado["valor_usdt"] == cantidad_actual * precio_actual
    assert resultado["precio_promedio_compra"] == Decimal("30000")
    assert resultado["costo_base_actual"] == cantidad_actual * Decimal("30000")
    assert resultado["ganancia_perdida"] == (cantidad_actual * precio_actual) - (cantidad_actual * Decimal("30000"))

# --- Tests para las funciones con I/O (refactorizados) ---

def test_estado_actual_completo_con_archivos_temporales(tmp_path):
    """
    Prueba [estado_actual_completo](cci:1://file:///Users/andreiveis/UADE/2do%20cuatrimestre/05_Algoritmos%20y%20Estructura%20de%20datos%20I/Trabajo_Simulador_Exchange/backend/servicios/estado_billetera.py:76:0-132:36) usando archivos temporales reales,
    eliminando la necesidad de mocks y fixtures de datos.
    """
    # 1. Preparación: Crear archivos de datos temporales
    ruta_billetera = tmp_path / "billetera.json"
    ruta_historial = tmp_path / "historial.json"
    ruta_cotizaciones = tmp_path / "cotizaciones.json"

    billetera_data = {
        "BTC": {"saldos": {"disponible": "1.5", "reservado": "0"}},
        "ETH": {"saldos": {"disponible": "2.0", "reservado": "0"}},
        "DOGE": {"saldos": {"disponible": "0", "reservado": "0"}}
    }
    historial_data = [
        {"tipo": "compra", "destino": {"ticker": "BTC", "cantidad": "1.0"}, "valor_usd": "30000"},
        {"tipo": "compra", "destino": {"ticker": "BTC", "cantidad": "0.5"}, "valor_usd": "15000"},
        {"tipo": "compra", "destino": {"ticker": "ETH", "cantidad": "2.0"}, "valor_usd": "20000"}
    ]
    cotizaciones_data = [
        {"ticker": "BTC", "nombre": "Bitcoin", "precio_usd": "40000", "logo": "logo_btc.png"},
        {"ticker": "ETH", "nombre": "Ethereum", "precio_usd": "1500", "logo": "logo_eth.png"}
    ]

    ruta_billetera.write_text(json.dumps(billetera_data), encoding='utf-8')
    ruta_historial.write_text(json.dumps(historial_data), encoding='utf-8')
    ruta_cotizaciones.write_text(json.dumps(cotizaciones_data), encoding='utf-8')

    # 2. Ejecución
    resultado_lista = estado_actual_completo(
        ruta_billetera=str(ruta_billetera),
        ruta_historial=str(ruta_historial),
        ruta_cotizaciones=str(ruta_cotizaciones)
    )

    # 3. Verificación
    assert isinstance(resultado_lista, list)
    assert len(resultado_lista) == 2
    assert resultado_lista[0]['ticker'] == 'BTC'
    assert resultado_lista[1]['ticker'] == 'ETH'
    assert not any(activo['ticker'] == 'DOGE' for activo in resultado_lista)

    btc = resultado_lista[0]
    eth = resultado_lista[1]

    assert btc["ticker"] == "BTC"
    assert btc["cantidad_total"] == "1.5"
    assert btc["valor_usdt_formatted"] == "$60,000.00"
    assert btc["logo"] == "logo_btc.png"
    assert btc["ganancia_perdida_formatted"] == "+$15,000.00"

    assert eth["ticker"] == "ETH"
    assert eth["cantidad_total"] == "2.0"
    assert eth["valor_usdt_formatted"] == "$3,000.00"
    assert eth["logo"] == "logo_eth.png"
    assert eth["ganancia_perdida_formatted"] == "-$17,000.00"

def test_obtener_historial_formateado_con_archivo_temporal(tmp_path):
    """
    Prueba que obtener_historial_formateado procese correctamente un
    archivo de historial temporal.
    """
    ruta_historial = tmp_path / "historial_test.json"
    historial_data = [
        {
            "id": "123", "tipo": "compra", "timestamp": "2023-10-27T10:00:00Z",
            "origen": {"ticker": "USDT"},
            "destino": {"ticker": "BTC", "cantidad": "0.5"},
            "valor_usd": "25000"
        }
    ]
    ruta_historial.write_text(json.dumps(historial_data), encoding='utf-8')

    resultado = obtener_historial_formateado(ruta_historial=str(ruta_historial))

    assert len(resultado) == 1
    item = resultado[0]
    assert item["id"] == "123"
    assert item["tipo_formatted"] == "Compra"
    assert item["par_formatted"] == "BTC/USDT"
    assert "27/10/2023" in item["fecha_formatted"]
    assert item["cantidad_formatted"] == "0.50000000 BTC"
    assert item["valor_total_formatted"] == "$25,000.00"