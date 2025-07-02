import pytest
import os
import json
import config

@pytest.fixture
def test_environment(tmp_path, monkeypatch):
    """
    Crea un entorno de prueba aislado con archivos de datos temporales.

    Este fixture crea un directorio temporal y redirige las constantes de ruta
    del módulo `config` para que apunten a archivos dentro de ese directorio.
    Esto asegura que los tests no lean ni modifiquen los datos reales de la aplicación.

    Uso:
        def mi_test(test_environment):
            # Ahora las funciones del backend usarán los archivos temporales.
            # ...
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
