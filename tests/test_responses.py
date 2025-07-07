"""
Pruebas Unitarias para las Utilidades de Respuesta.

Este archivo prueba que las funciones de ayuda en `backend.utils.responses`
construyen diccionarios de respuesta estandarizados y consistentes.
"""

from backend.utils.responses import crear_respuesta_exitosa, crear_respuesta_error

def test_crear_respuesta_exitosa():
    """
    Verifica que se cree una respuesta exitosa con la estructura correcta.
    """
    datos_payload = {"id": 1, "nombre": "Test"}
    mensaje_opcional = "Operación completada."
    
    respuesta = crear_respuesta_exitosa(datos_payload, mensaje_opcional)
    
    assert isinstance(respuesta, dict)
    assert respuesta["estado"] == "ok"
    assert respuesta["datos"] == datos_payload
    assert respuesta["mensaje"] == mensaje_opcional

def test_crear_respuesta_exitosa_sin_mensaje():
    """
    Verifica que una respuesta exitosa funciona correctamente sin un mensaje opcional.
    """
    datos_payload = [1, 2, 3]
    
    respuesta = crear_respuesta_exitosa(datos_payload)
    
    assert respuesta["estado"] == "ok"
    assert respuesta["datos"] == datos_payload
    assert respuesta["mensaje"] == "" # El valor por defecto debe ser un string vacío

def test_crear_respuesta_error():
    """
    Verifica que se cree una respuesta de error con la estructura correcta.
    """
    mensaje_error = "No se pudo encontrar el recurso."
    
    respuesta = crear_respuesta_error(mensaje_error)
    
    assert isinstance(respuesta, dict)
    assert respuesta["estado"] == "error"
    assert respuesta["mensaje"] == mensaje_error
    # Es importante verificar que no incluye la clave 'datos'
    assert "datos" not in respuesta