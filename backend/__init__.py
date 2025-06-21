"""
Paquete principal del backend de la aplicación.

Este archivo `__init__.py` no solo marca el directorio `backend` como un paquete de
Python, sino que también contiene la "Application Factory" `crear_app`.
Este patrón es una buena práctica en Flask que permite crear múltiples instancias
de la aplicación con diferentes configuraciones, facilitando las pruebas y la
escalabilidad.
"""

from flask import Flask
from config import FLASK_SECRET_KEY
from backend.rutas import registrar_rutas

def crear_app() -> Flask:
    """
    Crea, configura y devuelve una instancia de la aplicación Flask.

    Esta función sigue el patrón de diseño "Application Factory". Se encarga de:
    1. Crear la instancia de la aplicación Flask.
    2. Configurar la ubicación de las carpetas de plantillas y archivos estáticos.
    3. Establecer la clave secreta para la gestión de sesiones y mensajes flash.
    4. Registrar todos los blueprints (conjuntos de rutas) de la aplicación.

    Returns:
        Flask: La instancia de la aplicación Flask configurada y lista para usarse.
    """
    app = Flask(
        __name__,
        static_folder="../frontend/static",
        template_folder="../frontend/templates",
    )

    app.secret_key = FLASK_SECRET_KEY

    registrar_rutas(app)

    return app