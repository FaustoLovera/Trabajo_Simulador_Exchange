"""
Utilidades para estandarizar las respuestas de los servicios.
"""

def crear_respuesta_exitosa(datos, mensaje=""):
    """Crea una respuesta estandarizada para operaciones exitosas."""
    return {"estado": "ok", "datos": datos, "mensaje": mensaje}

def crear_respuesta_error(mensaje):
    """Crea una respuesta estandarizada para operaciones fallidas."""
    return {"estado": "error", "mensaje": mensaje}
