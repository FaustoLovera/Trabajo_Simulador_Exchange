import pytest
from decimal import Decimal
from backend.servicios.velas_logica import guardar_datos_cotizaciones, cargar_datos_cotizaciones


class TestVelasLogica:
    def test_guardar_datos_cotizaciones(self, monkeypatch):
        """
        Test para guardar_datos_cotizaciones con datos de muestra.
        """
        # Datos de muestra
        datos = [
            {
                'ticker': 'BTC',
                'nombre': 'Bitcoin',
                'precio_usd': Decimal('50000'),
                'market_cap': Decimal('1000000000'),
                'volumen_24h': Decimal('1000000')
            }
        ]

        # Mock de funciones externas
        def mock_makedirs(path, exist_ok):
            pass

        def mock_open(path, mode):
            return MockFile()

        class MockFile:
            def write(self, data):
                pass
            def close(self):
                pass

        monkeypatch.setattr('os.makedirs', mock_makedirs)
        monkeypatch.setattr('builtins.open', mock_open)

        # Ejecutar la función
        guardar_datos_cotizaciones(datos)

        # Verificar que los datos se guardaron correctamente
        # En este caso, solo podemos verificar que la función no lance excepciones
        # ya que estamos mockeando el archivo

    def test_cargar_datos_cotizaciones(self, monkeypatch):
        """
        Test para cargar_datos_cotizaciones.
        """
        # Datos de muestra a cargar
        datos = [
            {
                'ticker': 'BTC',
                'nombre': 'Bitcoin',
                'precio_usd': 50000.0
            }
        ]

        # Mock de funciones externas
        def mock_exists(path):
            return True

        def mock_open(path, mode):
            return MockFile(datos)

        class MockFile:
            def __init__(self, data):
                self.data = data

            def read(self):
                return json.dumps(self.data)

            def close(self):
                pass

        monkeypatch.setattr('os.path.exists', mock_exists)
        monkeypatch.setattr('builtins.open', mock_open)

        # Ejecutar la función
        resultado = cargar_datos_cotizaciones()

        # Verificar que los datos se cargaron correctamente
        assert len(resultado) == 1
        assert resultado[0]['ticker'] == 'BTC'
        assert resultado[0]['nombre'] == 'Bitcoin'
        assert resultado[0]['precio_usd'] == Decimal('50000')

    def test_cargar_datos_cotizaciones_archivo_no_existe(self, monkeypatch):
        """
        Test para cargar_datos_cotizaciones cuando el archivo no existe.
        """
        # Mock de funciones externas
        def mock_exists(path):
            return False

        monkeypatch.setattr('os.path.exists', mock_exists)

        # Ejecutar la función
        resultado = cargar_datos_cotizaciones()

        # Verificar que retorna una lista vacía
        assert resultado == []
