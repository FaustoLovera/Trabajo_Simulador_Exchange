import pytest
from decimal import Decimal
from backend.servicios.estado_billetera import estado_actual_completo, calcular_detalle_cripto


class TestEstadoBilletera:
    def test_estado_actual_completo(self, monkeypatch):
        """
        Test para estado_actual_completo con datos de muestra.
        """
        # Mock de funciones externas
        def mock_cargar_billetera():
            return {
                'BTC': Decimal('0.5'),
                'ETH': Decimal('2.0'),
                'USDT': Decimal('1000')
            }

        def mock_cargar_historial():
            return [
                {'moneda_origen': 'USDT', 'cantidad_origen': Decimal('20000'),
                 'moneda_destino': 'BTC', 'cantidad_destino': Decimal('0.5')},
                {'moneda_origen': 'USDT', 'cantidad_origen': Decimal('1000'),
                 'moneda_destino': 'ETH', 'cantidad_destino': Decimal('2.0')}
            ]

        def mock_obtener_precio(moneda):
            precios = {
                'BTC': Decimal('50000'),
                'ETH': Decimal('3000'),
                'USDT': Decimal('1')
            }
            return precios.get(moneda.upper(), Decimal('0'))

        def mock_cargar_datos_cotizaciones():
            return [
                {'ticker': 'BTC', 'nombre': 'Bitcoin', 'precio_usd': Decimal('50000')},
                {'ticker': 'ETH', 'nombre': 'Ethereum', 'precio_usd': Decimal('3000')}
            ]

        monkeypatch.setattr('backend.acceso_datos.datos_billetera.cargar_billetera', mock_cargar_billetera)
        monkeypatch.setattr('backend.acceso_datos.datos_historial.cargar_historial', mock_cargar_historial)
        monkeypatch.setattr('backend.acceso_datos.datos_cotizaciones.obtener_precio', mock_obtener_precio)
        monkeypatch.setattr('backend.acceso_datos.datos_cotizaciones.cargar_datos_cotizaciones', mock_cargar_datos_cotizaciones)

        # Ejecutar la función
        estado = estado_actual_completo()
        
        # Verificar que se calcula correctamente el estado de cada criptomoneda
        btc = next(item for item in estado if item['ticker'] == 'BTC')
        eth = next(item for item in estado if item['ticker'] == 'ETH')
        usdt = next(item for item in estado if item['ticker'] == 'USDT')

        # Verificar valores calculados para BTC
        assert btc['ticker'] == 'BTC'
        assert btc['nombre'] == 'Bitcoin'
        assert btc['cantidad'] == '0.5'
        assert btc['valor_usdt'] == '25000'
        assert btc['precio_actual'] == '50000'
        assert btc['precio_promedio'] == '40000'  # 20000 USDT / 0.5 BTC
        assert btc['invertido'] == '20000'
        assert btc['ganancia_perdida'] == '5000'
        assert btc['porcentaje_ganancia'] == '25'

        # Verificar valores calculados para ETH
        assert eth['ticker'] == 'ETH'
        assert eth['nombre'] == 'Ethereum'
        assert eth['cantidad'] == '2.0'
        assert eth['valor_usdt'] == '6000'
        assert eth['precio_actual'] == '3000'
        assert eth['precio_promedio'] == '500'    # 1000 USDT / 2 ETH
        assert eth['invertido'] == '1000'
        assert eth['ganancia_perdida'] == '5000'
        assert eth['porcentaje_ganancia'] == '500'

        # Verificar valores para USDT
        assert usdt['ticker'] == 'USDT'
        assert usdt['cantidad'] == '1000'
        assert usdt['valor_usdt'] == '1000'
        assert usdt['precio_actual'] == '1'

    def test_calcular_detalle_cripto(self):
        """
        Test para calcular_detalle_cripto con datos de muestra.
        """
        # Datos de muestra
        ticker = 'BTC'
        cantidad_actual = Decimal('0.5')
        precios = {
            'BTC': Decimal('50000'),
            'USDT': Decimal('1')
        }
        historial = [
            {'moneda_origen': 'USDT', 'cantidad_origen': Decimal('20000'),
             'moneda_destino': 'BTC', 'cantidad_destino': Decimal('0.5')}
        ]
        info_cripto = {
            'ticker': 'BTC',
            'nombre': 'Bitcoin'
        }

        # Ejecutar la función
        detalle = calcular_detalle_cripto(ticker, cantidad_actual, precios, historial, info_cripto)

        # Verificar que se calculan correctamente todas las métricas
        assert detalle['ticker'] == 'BTC'
        assert detalle['nombre'] == 'Bitcoin'
        assert detalle['cantidad'] == Decimal('0.5')
        assert detalle['valor_usdt'] == Decimal('25000')
        assert detalle['precio_actual'] == Decimal('50000')
        assert detalle['precio_promedio'] == Decimal('40000')
        assert detalle['invertido'] == Decimal('20000')
        assert detalle['ganancia_perdida'] == Decimal('5000')
        assert detalle['porcentaje_ganancia'] == Decimal('25')

    def test_calcular_detalle_cripto_sin_historial(self):
        """
        Test para calcular_detalle_cripto cuando no hay historial de transacciones.
        """
        ticker = 'BTC'
        cantidad_actual = Decimal('0.5')
        precios = {
            'BTC': Decimal('50000')
        }
        historial = []  # Sin historial
        info_cripto = {
            'ticker': 'BTC',
            'nombre': 'Bitcoin'
        }

        detalle = calcular_detalle_cripto(ticker, cantidad_actual, precios, historial, info_cripto)

        assert detalle['ticker'] == 'BTC'
        assert detalle['nombre'] == 'Bitcoin'
        assert detalle['cantidad'] == Decimal('0.5')
        assert detalle['valor_usdt'] == Decimal('25000')
        assert detalle['precio_actual'] == Decimal('50000')
        assert detalle['precio_promedio'] == Decimal('0')  # Sin historial, precio promedio es 0
        assert detalle['invertido'] == Decimal('0')
        assert detalle['ganancia_perdida'] == Decimal('25000')
        assert detalle['porcentaje_ganancia'] == Decimal('0')

    def test_calcular_detalle_cripto_cantidad_cero(self):
        """
        Test para calcular_detalle_cripto cuando la cantidad es cero.
        """
        ticker = 'BTC'
        cantidad_actual = Decimal('0')
        precios = {
            'BTC': Decimal('50000')
        }
        historial = [
            {'moneda_origen': 'USDT', 'cantidad_origen': Decimal('20000'),
             'moneda_destino': 'BTC', 'cantidad_destino': Decimal('0.5')}
        ]
        info_cripto = {
            'ticker': 'BTC',
            'nombre': 'Bitcoin'
        }

        detalle = calcular_detalle_cripto(ticker, cantidad_actual, precios, historial, info_cripto)

        assert detalle['ticker'] == 'BTC'
        assert detalle['nombre'] == 'Bitcoin'
        assert detalle['cantidad'] == Decimal('0')
        assert detalle['valor_usdt'] == Decimal('0')
        assert detalle['precio_actual'] == Decimal('50000')
        assert detalle['precio_promedio'] == Decimal('40000')
        assert detalle['invertido'] == Decimal('20000')
        assert detalle['ganancia_perdida'] == Decimal('-20000')
        assert detalle['porcentaje_ganancia'] == Decimal('-100')

    def test_calcular_detalle_cripto_precio_cero(self):
        """
        Test para calcular_detalle_cripto cuando el precio es cero.
        """
        ticker = 'BTC'
        cantidad_actual = Decimal('0.5')
        precios = {
            'BTC': Decimal('0')  # Precio cero
        }
        historial = [
            {'moneda_origen': 'USDT', 'cantidad_origen': Decimal('20000'),
             'moneda_destino': 'BTC', 'cantidad_destino': Decimal('0.5')}
        ]
        info_cripto = {
            'ticker': 'BTC',
            'nombre': 'Bitcoin'
        }

        detalle = calcular_detalle_cripto(ticker, cantidad_actual, precios, historial, info_cripto)

        assert detalle['ticker'] == 'BTC'
        assert detalle['nombre'] == 'Bitcoin'
        assert detalle['cantidad'] == Decimal('0.5')
        assert detalle['valor_usdt'] == Decimal('0')  # Valor en USD es cero cuando el precio es cero
        assert detalle['precio_actual'] == Decimal('0')
        assert detalle['precio_promedio'] == Decimal('40000')
        assert detalle['invertido'] == Decimal('20000')
        assert detalle['ganancia_perdida'] == Decimal('-20000')
        assert detalle['porcentaje_ganancia'] == Decimal('-100')