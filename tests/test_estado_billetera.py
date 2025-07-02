"""Pruebas Unitarias para el Servicio de Estado de Billetera.

Este archivo contiene pruebas para el módulo `backend.servicios.estado_billetera`,
que es responsable de calcular y formatear los datos consolidados de la billetera
para su presentación en la interfaz de usuario.

Las pruebas se dividen en dos categorías principales:
1.  **Pruebas de Funciones Puras**: Verifican la lógica de negocio de las
    funciones de cálculo (`_preparar_datos_compra`, `_calcular_metricas_activo`)
    de forma aislada, sin depender de I/O. Estas pruebas son rápidas y cubren
    diversos casos de borde.
2.  **Pruebas de Integración con I/O**: Verifican las funciones principales
    (`estado_actual_completo`, `obtener_historial_formateado`) que orquestan
    la lectura de datos desde archivos. Utilizan la fixture `tmp_path` de pytest
    para interactuar con archivos reales en un entorno temporal y aislado.
"""

import pytest
import json
from decimal import Decimal

from backend.servicios.estado_billetera import (
    _calcular_metricas_activo,
    _preparar_datos_compra,
    estado_actual_completo,
    obtener_historial_formateado
)

# --- Fixtures: Datos de prueba reutilizables ---

@pytest.fixture
def datos_compra_btc():
    """Proporciona un diccionario de ejemplo con datos de compra para BTC.

    Este fixture simula el resultado agregado de la función `_preparar_datos_compra`
    para un activo específico. Es utilizado por las pruebas que calculan métricas
    para desacoplarlas de la lógica de preparación de datos.

    Returns:
        dict: Un diccionario con el total invertido y la cantidad comprada.
    """
    return {
        "total_invertido": Decimal("45000"),
        "cantidad_comprada": Decimal("1.5")
    }

# --- Tests para las funciones puras (sin cambios, no dependen de I/O) ---

def test_preparar_datos_compra_debe_procesar_solo_compras_y_agrupar_por_ticker_cuando_historial_es_mixto():
    """Verifica que se procese un historial mixto correctamente.

    Esta prueba asegura que la función:
    -   Filtra y procesa únicamente las transacciones de tipo 'compra'.
    -   Ignora las transacciones de 'venta' y otros tipos.
    -   Excluye el ticker 'USDT', ya que no se considera una inversión.
    -   Agrupa los resultados por ticker.
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

def test_preparar_datos_compra_debe_retornar_diccionario_vacio_cuando_historial_esta_vacio():
    """Verifica el comportamiento con una lista de historial vacía.

    Prueba el caso de borde donde no hay transacciones. Se espera que la función
    devuelva un diccionario vacío sin errores.
    """
    resultado = _preparar_datos_compra([])
    assert resultado == {}

def test_preparar_datos_compra_debe_retornar_diccionario_vacio_cuando_historial_no_contiene_compras():
    """Verifica el comportamiento con un historial que no contiene compras.

    Prueba el caso donde existen transacciones, pero ninguna es de tipo 'compra'.
    Se espera que la función devuelva un diccionario vacío.
    """
    historial = [
        {"tipo": "venta", "destino": {"ticker": "BTC", "cantidad": "1.0"}, "valor_usd": "30000"},
        {"tipo": "transferencia", "destino": {"ticker": "ETH", "cantidad": "2.0"}, "valor_usd": "20000"},
    ]
    resultado = _preparar_datos_compra(historial)
    assert resultado == {}

def test_preparar_datos_compra_debe_sumarizar_valores_cuando_hay_multiples_compras_del_mismo_activo():
    """Verifica que se agrupen múltiples compras del mismo activo.

    Esta prueba asegura que la función suma correctamente el `total_invertido`
    y la `cantidad_comprada` de varias transacciones de compra para un único
    ticker.
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


def test_calcular_metricas_activo_debe_retornar_calculos_correctos_cuando_recibe_datos_validos(datos_compra_btc):
    """Verifica el cálculo de todas las métricas de rendimiento para un activo.

    Esta prueba utiliza datos de entrada fijos (cantidad actual, precio actual
    y datos de compra desde una fixture) para verificar que todos los cálculos
    derivados (valor total, precio promedio, costo base, ganancia/pérdida)
    son correctos.

    Args:
        datos_compra_btc: Fixture con datos de compra agregados para BTC.
    """
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

def test_estado_actual_completo_debe_generar_reporte_consolidado_cuando_lee_archivos_de_datos(tmp_path):
    """Prueba de integración para `estado_actual_completo` con archivos reales.

    Este test verifica el flujo completo de la función, que orquesta la lectura
    de múltiples archivos JSON (billetera, historial, cotizaciones) para generar
    el estado consolidado de la billetera.

    El uso de `tmp_path` permite crear un entorno de prueba realista y aislado:
    1.  **Arrange**: Se escriben archivos `billetera.json`, `historial.json` y
        `cotizaciones.json` con datos de prueba en un directorio temporal.
    2.  **Act**: Se llama a `estado_actual_completo` apuntando a estas rutas temporales.
    3.  **Assert**: Se verifica que el resultado final sea correcto, incluyendo:
        - Que solo se incluyan activos con saldo.
        - Que los cálculos y el formato de los datos sean los esperados.

    Args:
        tmp_path: Fixture de pytest que proporciona una ruta a un directorio temporal.
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
    assert btc["valor_usdt_formatted"] == "$60,000"
    assert btc["logo"] == "logo_btc.png"
    assert btc["ganancia_perdida_formatted"] == "$15,000"

    assert eth["ticker"] == "ETH"
    assert eth["cantidad_total"] == "2.0"
    assert eth["valor_usdt_formatted"] == "$3,000"
    assert eth["logo"] == "logo_eth.png"
    assert eth["ganancia_perdida_formatted"] == "$-17,000"

def test_obtener_historial_formateado_debe_aplicar_formato_de_presentacion_cuando_lee_historial(tmp_path):
    """Prueba de integración para `obtener_historial_formateado`.

    Verifica que la función lee correctamente un archivo de historial y aplica
    el formato esperado a cada campo para su visualización en la interfaz.

    Flujo de la prueba:
    1.  **Arrange**: Se crea un archivo `historial.json` temporal con un registro.
    2.  **Act**: Se llama a `obtener_historial_formateado`.
    3.  **Assert**: Se comprueba que los campos clave (`tipo`, `par`, `fecha`, etc.)
        hayan sido transformados al formato de presentación correcto.

    Args:
        tmp_path: Fixture de pytest que proporciona una ruta a un directorio temporal.
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
    assert item["cantidad_formatted"] == "0.5"
    assert item["valor_total_formatted"] == "$25,000"