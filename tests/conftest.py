"""Configuración Global de Pruebas y Fixtures Compartidas para Pytest.

Este archivo, `conftest.py`, es un mecanismo especial de `pytest` para definir
fixtures, hooks y plugins que estarán disponibles globalmente en toda la suite
de pruebas. Su propósito es centralizar la configuración y los datos de prueba,
promoviendo la reutilización de código y manteniendo los tests limpios y enfocados.

Las fixtures definidas aquí preparan un entorno de prueba controlado y aislado,
fundamental para garantizar que las pruebas sean deterministas y no tengan
efectos secundarios sobre el entorno real o entre ellas.
"""

import pytest
import os
import json
import config
from backend.acceso_datos.datos_cotizaciones import limpiar_cache_precios

@pytest.fixture
def test_environment(tmp_path, monkeypatch):
    """Fixture para crear un entorno de prueba completamente aislado.

    Esta fixture es la base para la mayoría de las pruebas. Realiza dos acciones clave
    para garantizar que cada test se ejecute en un 'sandbox' limpio:

    1.  **Sistema de Archivos Temporal (`tmp_path`)**: Crea un directorio temporal
        único para esta ejecución de prueba. Todos los archivos de datos
        (billetera, historial, etc.) se crean dentro de este directorio.
        `pytest` se encarga de eliminarlo automáticamente al finalizar la prueba.

    2.  **Redirección de Configuración (`monkeypatch`)**: Modifica en tiempo de
        ejecución las variables de ruta del módulo `config` (ej. `config.BILLETERA_PATH`)
        para que apunten a los archivos en `tmp_path`. Esto asegura que el código
        de la aplicación, al ser probado, opere sobre los datos de prueba y no
        sobre los datos reales.

    Yields:
        Dict[str, str]: Un diccionario con las rutas a los archivos de datos
                        temporales, por si alguna prueba necesita acceder a ellos
                        directamente.
    """
    # Crear un subdirectorio para los datos de prueba para mayor orden
    datos_dir = tmp_path / "datos_test"
    datos_dir.mkdir()

    # Rutas a los archivos temporales
    billetera_path = datos_dir / "billetera.json"
    historial_path = datos_dir / "historial.json"
    ordenes_path = datos_dir / "ordenes_pendientes.json"
    cotizaciones_path = datos_dir / "cotizaciones.json"
    comisiones_path = datos_dir / "comisiones.json"

    # Redirigir las constantes del módulo config usando monkeypatch
    monkeypatch.setattr(config, 'BILLETERA_PATH', str(billetera_path))
    monkeypatch.setattr(config, 'HISTORIAL_PATH', str(historial_path))
    monkeypatch.setattr(config, 'ORDENES_PENDIENTES_PATH', str(ordenes_path))
    monkeypatch.setattr(config, 'COTIZACIONES_PATH', str(cotizaciones_path))
    monkeypatch.setattr(config, 'COMISIONES_PATH', str(comisiones_path))

    # Se puede inicializar archivos si es necesario, por ejemplo:
    with open(billetera_path, 'w') as f:
        json.dump({}, f)
    with open(historial_path, 'w') as f:
        json.dump([], f)
    with open(ordenes_path, 'w') as f:
        json.dump([], f)
    with open(cotizaciones_path, 'w') as f:
        json.dump([], f)
    with open(comisiones_path, 'w') as f:
        json.dump({}, f)

    # El fixture puede devolver las rutas si algún test las necesita
    yield {
        "billetera": str(billetera_path),
        "historial": str(historial_path),
        "ordenes": str(ordenes_path),
        "cotizaciones": str(cotizaciones_path),
        "comisiones": str(comisiones_path)
    }

    # La limpieza es automática gracias a tmp_path


@pytest.fixture(autouse=True)
def limpiar_cache_cada_vez():
    """Fixture autoejecutable que limpia la caché de precios antes de cada test.

    Al usar `autouse=True`, esta fixture se invoca automáticamente para cada
    función de prueba, garantizando que el estado de la caché no se filtre
    entre tests. Esto es crucial para mantener el aislamiento y la
    fiabilidad de la suite de pruebas.

    Yields:
        None: No devuelve ningún valor, solo realiza la acción de limpieza.
    """
    limpiar_cache_precios()
    yield
    limpiar_cache_precios() # Limpiar también después, por si acaso


@pytest.fixture
def entorno_con_orden_pendiente(test_environment):
    """Fixture que prepara un escenario con una orden de venta pendiente.

    Esta fixture se basa en `test_environment` para obtener un entorno aislado
    y luego lo puebla con datos específicos para simular un escenario común:

    -   **Billetera**: Contiene 1.0 BTC disponible y 0.5 BTC reservados.
    -   **Órdenes Pendientes**: Existe una orden de venta por 0.5 BTC.

    Es ideal para probar funcionalidades como la cancelación de órdenes o la
    correcta visualización de saldos reservados.

    Args:
        test_environment: La fixture base que provee el entorno aislado.

    Returns:
        El mismo diccionario de rutas que `test_environment`.
    """
    billetera_data = {
        "BTC": {"saldos": {"disponible": "1.0", "reservado": "0.5"}}
    }
    ordenes_data = [
        {"id_orden": "btc_venta_1", "estado": "pendiente", "moneda_reservada": "BTC", "cantidad_reservada": "0.5", "par": "BTC/USDT"}
    ]
    
    with open(config.BILLETERA_PATH, 'w') as f:
        json.dump(billetera_data, f)
    with open(config.ORDENES_PENDIENTES_PATH, 'w') as f:
        json.dump(ordenes_data, f)
        
    return test_environment


@pytest.fixture
def billetera_con_fondos_suficientes(test_environment):
    """Prepara un entorno con una billetera que tiene fondos amplios.

    - USDT: 10000.0
    - BTC: 5.0
    """
    billetera_data = {
        "USDT": {"nombre": "Tether", "saldos": {"disponible": "10000.0", "reservado": "0.0"}},
        "BTC": {"nombre": "Bitcoin", "saldos": {"disponible": "5.0", "reservado": "0.0"}}
    }
    with open(config.BILLETERA_PATH, 'w') as f:
        json.dump(billetera_data, f)
    
    return test_environment

@pytest.fixture
def billetera_con_fondos_insuficientes(test_environment):
    """Prepara un entorno con una billetera con fondos limitados.

    - USDT: 500.0
    """
    billetera_data = {
        "USDT": {"nombre": "Tether", "saldos": {"disponible": "500.0", "reservado": "0.0"}}
    }
    with open(config.BILLETERA_PATH, 'w') as f:
        json.dump(billetera_data, f)
        
    return test_environment
