"""
Pruebas de Integración para los Endpoints de la Aplicación Flask.

Este archivo prueba las rutas de la aplicación utilizando el cliente de pruebas
de Flask. El objetivo es verificar que cada endpoint responde correctamente a las
peticiones HTTP, maneja los datos de entrada y devuelve los códigos de estado
y los datos esperados.

Estas pruebas cubren la capa de vista (rutas) y su interacción con la capa de
servicios, asegurando que toda la aplicación funciona de forma integrada.
"""

import json
from decimal import Decimal


def test_ruta_home_devuelve_status_200(client):
    """Verifica que la página de inicio se carga correctamente."""
    response = client.get('/')
    assert response.status_code == 200
    # Verifica que el HTML contiene un texto esperado
    assert b"Cotizaciones" in response.data

def test_ruta_trading_operar_exitosa_redirige(client, test_environment):
    """
    Verifica que una operación de trading exitosa (orden límite) a través
    de la ruta /trading/operar:
    1. Responde con un código de redirección (302).
    2. Modifica correctamente los archivos de estado (billetera y órdenes).
    """
    # ARRANGE: Preparar los archivos necesarios para la operación.

    billetera_inicial = {
        "USDT": {"nombre": "Tether", "saldos": {"disponible": "10000", "reservado": "0"}},
        "BTC": {"nombre": "Bitcoin", "saldos": {"disponible": "1", "reservado": "0"}}
    }
    try:
        with open(test_environment['billetera'], 'w') as f:
            json.dump(billetera_inicial, f, indent=4)
    except FileNotFoundError:
        pass

    # El formulario que el frontend enviaría
    formulario = {
        "ticker": "BTC",
        "accion": "compra",
        "monto": "500",
        "modo-ingreso": "total",
        "tipo-orden": "limit",
        "precio_disparo": "20000"
    }

    # ACT: Simular una petición POST a la ruta de operaciones.
    response = client.post('/trading/operar', data=formulario)

    # ASSERT
    # 1. Verificar la respuesta HTTP.
    assert response.status_code == 302
    assert response.location.startswith('/trading')

    # 2. Verificar los efectos secundarios en los archivos.
    try:
        with open(test_environment['billetera'], 'r') as f:
            billetera_final = json.load(f)
    except FileNotFoundError:
        pass
    assert Decimal(billetera_final["USDT"]["saldos"]["disponible"]) == Decimal("9500")
    assert Decimal(billetera_final["USDT"]["saldos"]["reservado"]) == Decimal("500")

    try:
        with open(test_environment['ordenes'], 'r') as f:
            ordenes_pendientes = json.load(f)
    except FileNotFoundError:
        pass
    assert len(ordenes_pendientes) == 1
    assert ordenes_pendientes[0]["par"] == "BTC/USDT"

def test_ruta_trading_operar_falla_por_saldo_insuficiente(client, test_environment):
    """
    Verifica que una operación fallida por saldo insuficiente también redirige,
    pero no modifica los archivos de estado.
    """
    # ARRANGE: Billetera con fondos insuficientes.
    billetera_inicial = {
        "USDT": {"nombre": "Tether", "saldos": {"disponible": "100", "reservado": "0"}}
    }
    try:
        with open(test_environment['billetera'], 'w') as f:
            json.dump(billetera_inicial, f, indent=4)
    except FileNotFoundError:
        pass
        
    formulario = {"ticker": "BTC", "accion": "compra", "monto": "500",
                  "modo-ingreso": "total", "tipo-orden": "limit", "precio_disparo": "20000"}

    # ACT
    response = client.post('/trading/operar', data=formulario)

    # ASSERT
    # 1. La respuesta sigue siendo una redirección.
    assert response.status_code == 302
    
    # 2. Los archivos NO deben haber sido modificados.
    try:
        with open(test_environment['billetera'], 'r') as f:
            billetera_final = json.load(f)
    except FileNotFoundError:
        pass
    assert billetera_final == billetera_inicial # Ningún cambio

    try:
        with open(test_environment['ordenes'], 'r') as f:
            ordenes_pendientes = json.load(f)
    except FileNotFoundError:
        pass
    assert len(ordenes_pendientes) == 0 # Ninguna orden creada

def test_ruta_api_ordenes_abiertas_devuelve_json(client, test_environment):
    """Verifica que el endpoint de API /api/ordenes-abiertas funciona."""
    # ARRANGE: Crear una orden pendiente para que el endpoint la devuelva.
    orden_pendiente = {
        "id_orden": "test-123", "estado": "pendiente", "par": "ETH/USDT"
    }
    try:
        with open(test_environment['ordenes'], 'w') as f:
            json.dump([orden_pendiente], f)
    except FileNotFoundError:
        pass

    # ACT: Simular una petición GET al endpoint de la API.
    response = client.get('/api/ordenes-abiertas')

    # ASSERT
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['id_orden'] == 'test-123'