"""Pruebas Unitarias para el Módulo de Acceso a Datos de Cotizaciones.

Este archivo contiene un conjunto de pruebas unitarias para el módulo
`backend.acceso_datos.datos_cotizaciones`. El objetivo es verificar la
correcta interacción con el sistema de archivos para la persistencia
de los datos de cotizaciones.

Las pruebas aseguran que:
- Los datos se guardan y cargan correctamente en formato JSON.
- El sistema maneja de forma robusta casos de error, como archivos no encontrados.
- La caché de precios en memoria se actualiza correctamente como un efecto
  secundario de la escritura de datos.

Todas las pruebas utilizan un entorno aislado (`test_environment` fixture) para
no interferir con los datos reales de la aplicación.
"""

import json
from decimal import Decimal

import pytest
import config
from pathlib import Path

from backend.acceso_datos.datos_cotizaciones import (
    cargar_datos_cotizaciones,
    guardar_datos_cotizaciones,
    obtener_precio,
    recargar_cache_precios
)

def test_guardar_y_cargar_datos_cotizaciones_debe_persistir_y_recuperar_datos_cuando_se_usa_ruta_valida(test_environment):
    recargar_cache_precios() # Limpiar cache al inicio
    """Verifica el ciclo completo de guardar y cargar datos de cotizaciones.

    Esta prueba asegura que la funcionalidad básica de persistencia funciona
    correctamente. El flujo de la prueba es el siguiente:

    1.  **Preparación**: Se define una lista de datos de cotizaciones de prueba.
    2.  **Ejecución (Guardado)**: Se llama a `guardar_datos_cotizaciones`. La fixture
        `test_environment` garantiza que esta operación escribe en un archivo
        temporal y aislado, no en el archivo real de la aplicación.
    3.  **Verificación (Guardado)**: Se comprueba que el archivo temporal fue creado
        y que su contenido en formato JSON es el esperado.
    4.  **Ejecución (Cargado)**: Se llama a `cargar_datos_cotizaciones`, que leerá
        del mismo archivo temporal.
    5.  **Verificación (Cargado)**: Se asegura que los datos cargados en memoria
        son idénticos a los que se escribieron.

    Args:
        test_environment: Fixture que provee un entorno de prueba aislado.
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

def test_cargar_datos_cotizaciones_debe_retornar_lista_vacia_cuando_archivo_no_existe(test_environment):
    recargar_cache_precios() # Limpiar cache

    # Nos aseguramos de que el archivo no exista en el entorno temporal
    ruta_temporal = Path(test_environment['cotizaciones'])
    if ruta_temporal.exists():
        ruta_temporal.unlink()
    """Verifica que la carga de datos es robusta ante un archivo inexistente.

    Esta prueba simula un escenario de error común: el archivo de cotizaciones
    aún no ha sido creado o ha sido eliminado. Se espera que la función
    `cargar_datos_cotizaciones` maneje esta situación de forma segura,
    devolviendo una lista vacía en lugar de lanzar una excepción.

    Se utiliza `monkeypatch` para forzar que la ruta de configuración apunte
    a una ubicación garantizada de no existir.

    Args:
        monkeypatch: Fixture de pytest para modificar objetos en tiempo de ejecución.
    """

    resultado = cargar_datos_cotizaciones()
    assert resultado == []

def test_guardar_datos_cotizaciones_debe_actualizar_cache_de_precios_cuando_se_guardan_nuevos_datos(test_environment):
    """Verifica que guardar cotizaciones actualiza la caché de precios en memoria.

    Esta es una prueba de integración clave entre la capa de persistencia y la
    caché de acceso rápido en memoria. Comprueba un efecto secundario crucial:
    después de llamar a `guardar_datos_cotizaciones`, la caché interna debe
    ser invalidada y recargada, de modo que `obtener_precio` refleje
    inmediatamente los nuevos valores.

    Flujo de la prueba:
    1.  Se asegura que la caché está inicialmente vacía.
    2.  Se guardan nuevos datos de cotización.
    3.  Se verifica que `obtener_precio` ahora devuelve el precio recién guardado,
        confirmando que la caché se actualizó.

    Args:
        test_environment: Fixture que provee un entorno de prueba aislado.
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