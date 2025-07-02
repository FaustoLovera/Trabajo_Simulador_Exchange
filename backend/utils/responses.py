"""Funciones de ayuda para crear respuestas de servicio estandarizadas.

Este módulo proporciona constructores para generar respuestas consistentes
a través de la capa de servicios, asegurando que el frontend o cualquier
consumidor de la API reciba siempre un diccionario con una estructura predecible.
"""

from typing import Any, Dict

def crear_respuesta_exitosa(datos: Any, mensaje: str = "") -> Dict[str, Any]:
    """Crea una respuesta estandarizada para una operación exitosa.

    Genera un diccionario con el estado 'ok', los datos resultantes y un
    mensaje opcional.

    Args:
        datos (Any): Los datos a devolver en la respuesta (payload).
        mensaje (str, optional): Un mensaje descriptivo. Por defecto "".

    Returns:
        Dict[str, Any]: Un diccionario con las claves 'estado', 'datos' y 'mensaje'.
    """
    return {"estado": "ok", "datos": datos, "mensaje": mensaje}

def crear_respuesta_error(mensaje: str) -> Dict[str, Any]:
    """Crea una respuesta estandarizada para una operación fallida.

    Genera un diccionario con el estado 'error' y un mensaje descriptivo.

    Args:
        mensaje (str): El mensaje de error que explica la falla.

    Returns:
        Dict[str, Any]: Un diccionario con las claves 'estado' y 'mensaje'.
    """
    return {"estado": "error", "mensaje": mensaje}
