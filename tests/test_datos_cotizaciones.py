import json
from decimal import Decimal

# La importación se corrige para apuntar al móduloimport json
import pytest
import config
from pathlib import Path

from backend.acceso_datos.datos_cotizaciones import (
    cargar_datos_cotizaciones,
    guardar_datos_cotizaciones,
    obtener_precio,
    recargar_cache_precios
)

def test_guardar_y_cargar_datos_cotizaciones_con_ruta_temporal(test_environment):
    """
    Prueba que se puedan guardar y luego cargar datos de cotizaciones
    usando un archivo temporal gestionado por el fixture.
    """
    # 1. Preparación: Los datos se guardarán en la ruta gestionada por el fixture.
    datos_a_guardar = [
        {'ticker': 'BTC', 'nombre': 'Bitcoin', 'precio_usd': "50000.12345678"},
        {'ticker': 'ETH', 'nombre': 'Ethereum', 'precio_usd': "3000.87654321"}
    ]

    # 2. Ejecución (Guardar): la función usará la ruta parcheada por el fixture.
    guardar_datos_cotizaciones(datos_a_guardar)

    # 3. Verificación (Guardar): comprobamos que el archivo se escribió correctamente.
    ruta_temporal = Path(test_environment['cotizaciones'])
    assert ruta_temporal.exists()
    datos_leidos_raw = json.loads(ruta_temporal.read_text(encoding='utf-8'))
    
    assert len(datos_leidos_raw) == 2
    assert datos_leidos_raw[0]['precio_usd'] == "50000.12345678"

    # 4. Ejecución (Cargar): leemos desde la misma ruta temporal.
    datos_cargados = cargar_datos_cotizaciones()

    # 5. Verificación (Cargar): comprobamos que los datos se cargaron correctamente.
    assert datos_cargados == datos_leidos_raw

def test_cargar_datos_cotizaciones_archivo_no_existente(monkeypatch):
    """
    Prueba que `cargar_datos_cotizaciones` devuelva una lista vacía si el
    archivo especificado no existe.
    """
    # Forzamos que la ruta apunte a un archivo que no existe
    monkeypatch.setattr(config, 'COTIZACIONES_PATH', './ruta/inexistente.json')
    resultado = cargar_datos_cotizaciones()
    assert resultado == []

def test_guardar_datos_actualiza_cache_correctamente(test_environment):
    """
    Verifica que guardar nuevas cotizaciones en un archivo actualiza 
    correctamente el caché de precios global que usa `obtener_precio`.
    """
    # 1. Preparación:
    # El fixture `test_environment` ya ha redirigido la ruta a un archivo temporal
    # y lo ha creado vacío. Forzamos una recarga para asegurar que el caché esté vacío.
    recargar_cache_precios()
    assert obtener_precio('TESTCOIN') is None

    # 2. Ejecución:
    # Guardamos datos de prueba. El fixture asegura que se usa el archivo temporal.
    datos_test = [{'ticker': 'TESTCOIN', 'nombre': 'Test Coin', 'precio_usd': "9999"}]
    guardar_datos_cotizaciones(datos_test)

    # 3. Verificación:
    # La función `guardar_datos_cotizaciones` debe haber recargado el caché global.
    # Ahora, `obtener_precio` debe devolver el nuevo valor.
    assert obtener_precio('TESTCOIN') == Decimal("9999")