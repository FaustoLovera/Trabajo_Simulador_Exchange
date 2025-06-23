import pytest
from decimal import Decimal

# Importamos las funciones a probar
from backend.servicios.estado_billetera import _calcular_metricas_activo, estado_actual_completo

# --- Fixtures: Datos de prueba reutilizables ---

@pytest.fixture
def datos_compra_btc():
    """Fixture que proporciona datos de compra para Bitcoin."""
    return {
        "total_invertido": Decimal("45000"),
        "cantidad_comprada": Decimal("1.5")
    }

@pytest.fixture
def mock_billetera_data():
    """Fixture con datos simulados de la billetera."""
    return [
        {"ticker": "BTC", "cantidad": "1.5"},
        {"ticker": "ETH", "cantidad": "2.0"}
    ]

@pytest.fixture
def mock_historial_data():
    """Fixture con datos simulados del historial de transacciones."""
    return [
        {"tipo": "compra", "destino": {"ticker": "BTC", "cantidad": "1.0"}, "valor_usd": "30000"},
        {"tipo": "compra", "destino": {"ticker": "BTC", "cantidad": "0.5"}, "valor_usd": "15000"},
        {"tipo": "compra", "destino": {"ticker": "ETH", "cantidad": "2.0"}, "valor_usd": "20000"}
    ]

@pytest.fixture
def mock_cotizaciones_data():
    """Fixture con datos simulados de cotizaciones."""
    return {
        "BTC": Decimal("40000"),
        "ETH": Decimal("1500")
    }


# --- Tests para las funciones ---

def test_calcular_metricas_activo(datos_compra_btc):
    """Prueba la función de cálculo de métricas para un activo."""
    # Arrange: Preparación de datos
    ticker = "BTC"
    cantidad_actual = Decimal("1.5")
    precio_actual = Decimal("40000")
    
    # Act: Ejecución de la función
    resultado = _calcular_metricas_activo(ticker, cantidad_actual, precio_actual, datos_compra_btc)

    # Assert: Verificación de resultados con `assert`
    assert resultado["ticker"] == "BTC"
    assert resultado["cantidad"] == cantidad_actual
    assert resultado["precio_actual"] == precio_actual
    assert resultado["valor_usdt"] == cantidad_actual * precio_actual
    assert resultado["precio_promedio_compra"] == Decimal("30000")
    assert resultado["costo_base_actual"] == cantidad_actual * Decimal("30000")
    assert resultado["ganancia_perdida"] == (cantidad_actual * precio_actual) - (cantidad_actual * Decimal("30000"))

def test_estado_actual_completo(monkeypatch, mock_billetera_data, mock_historial_data, mock_cotizaciones_data):
    """
    Prueba la función orquestadora `estado_actual_completo` mockeando
    sus dependencias de acceso a datos.
    """
    # Arrange: Configuración de los mocks usando monkeypatch
    monkeypatch.setattr('backend.acceso_datos.datos_billetera.cargar_billetera', lambda: mock_billetera_data)
    monkeypatch.setattr('backend.acceso_datos.datos_historial.cargar_historial', lambda: mock_historial_data)
    monkeypatch.setattr('backend.acceso_datos.datos_cotizaciones.cargar_datos_cotizaciones', lambda: mock_cotizaciones_data)

    # Act: Ejecución de la función
    resultado = estado_actual_completo()

    # Assert: Verificación de resultados
    assert isinstance(resultado, dict)
    assert "BTC" in resultado
    assert "ETH" in resultado
    
    # Verificar cálculos para BTC
    btc = resultado["BTC"]
    assert btc["ticker"] == "BTC"
    assert btc["cantidad"] == Decimal("1.5")
    assert btc["precio_actual"] == Decimal("40000")
    
    # Verificar cálculos para ETH
    eth = resultado["ETH"]
    assert eth["ticker"] == "ETH"
    assert eth["cantidad"] == Decimal("2.0")
    assert eth["precio_actual"] == Decimal("1500")