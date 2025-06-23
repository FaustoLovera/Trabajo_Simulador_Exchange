import pytest
import json
import io  # Usaremos io.StringIO para simular archivos de texto de forma más limpia
from decimal import Decimal
from backend.servicios.velas_logica import guardar_datos_cotizaciones, cargar_datos_cotizaciones

# --- Test para guardar_datos_cotizaciones ---

def test_guardar_datos_cotizaciones(monkeypatch):
    """
    Prueba que `guardar_datos_cotizaciones` intente crear el directorio
    y escribir los datos correctos en el archivo.
    """
    # 1. Datos de muestra que se pasarán a la función
    datos_a_guardar = [
        {'ticker': 'BTC', 'nombre': 'Bitcoin', 'precio_usd': Decimal('50000')}
    ]
    
    # 2. Variables para capturar las llamadas a los mocks
    # Usaremos listas para poder modificarlas desde dentro de las funciones mock
    ruta_makedirs_llamada = []
    datos_escritos = []

    # 3. Mocks de las funciones del sistema de archivos
    def mock_makedirs(path, exist_ok=False):
        # Capturamos la ruta con la que se llamó a makedirs
        ruta_makedirs_llamada.append(path)
        assert exist_ok is True

    def mock_open_para_escritura(file, mode):
        # Verificamos que se intente abrir el archivo en modo escritura ('w')
        assert 'w' in mode
        # Simulamos un objeto archivo que captura lo que se escribe
        class MockFileWriter:
            def write(self, data):
                datos_escritos.append(data)
            def __enter__(self):
                return self
            def __exit__(self, type, value, traceback):
                pass
        return MockFileWriter()

    # 4. Aplicamos los mocks
    monkeypatch.setattr('os.makedirs', mock_makedirs)
    # Usamos 'builtins.open' para mockear la función open() global
    monkeypatch.setattr('builtins.open', mock_open_para_escritura)

    # 5. Ejecutamos la función a probar
    guardar_datos_cotizaciones(datos_a_guardar)
    
    # 6. Verificamos los resultados
    # Comprobamos que se intentó crear la carpeta 'datos'
    assert ruta_makedirs_llamada and 'datos' in str(ruta_makedirs_llamada[0])
    
    # Comprobamos que lo que se escribió en el archivo es el JSON correcto
    # Convertimos el string JSON escrito de vuelta a un objeto Python para compararlo
    assert len(datos_escritos) == 1
    datos_guardados = json.loads(datos_escritos[0])
    # Como JSON no tiene tipo Decimal, lo comparamos como string
    assert datos_guardados[0]['precio_usd'] == '50000'
    assert datos_guardados[0]['ticker'] == 'BTC'


# --- Tests para cargar_datos_cotizaciones ---

def test_cargar_datos_cotizaciones_cuando_archivo_existe(monkeypatch):
    """
    Prueba que `cargar_datos_cotizaciones` lea y procese correctamente
    un archivo JSON cuando este existe.
    """
    # 1. Datos que simularemos que están en el archivo
    contenido_json_mock = json.dumps([
        {'ticker': 'BTC', 'nombre': 'Bitcoin', 'precio_usd': '50000.0'}
    ])
    
    # 2. Mocks
    # Simulamos que el archivo SÍ existe
    monkeypatch.setattr('os.path.exists', lambda path: True)
    
    # Simulamos la apertura del archivo, devolviendo nuestro contenido mock
    # io.StringIO es perfecto para simular un archivo de texto en memoria
    monkeypatch.setattr('builtins.open', lambda file, mode: io.StringIO(contenido_json_mock))
    
    # 3. Ejecutamos la función
    resultado = cargar_datos_cotizaciones()
    
    # 4. Verificamos los resultados
    assert len(resultado) == 1
    assert resultado[0]['ticker'] == 'BTC'
    assert resultado[0]['nombre'] == 'Bitcoin'
    # La función debe convertir el string del JSON a Decimal
    assert resultado[0]['precio_usd'] == Decimal('50000.0')

def test_cargar_datos_cotizaciones_cuando_archivo_no_existe(monkeypatch):
    """
    Prueba que `cargar_datos_cotizaciones` devuelva una lista vacía
    si el archivo de datos no existe.
    """
    # 1. Mock: Simulamos que el archivo NO existe
    monkeypatch.setattr('os.path.exists', lambda path: False)
    
    # 2. Ejecutamos la función
    resultado = cargar_datos_cotizaciones()
    
    # 3. Verificamos el resultado
    assert resultado == []