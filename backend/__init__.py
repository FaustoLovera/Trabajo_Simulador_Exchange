"""Fábrica de la aplicación Flask (Application Factory).

Este archivo contiene la función `crear_app`, que implementa el patrón
"Application Factory". Este enfoque es una buena práctica en Flask para
desacoplar la creación de la aplicación, facilitando las pruebas y la
gestión de múltiples configuraciones.
"""

from flask import Flask
import config
from backend.rutas import registrar_rutas

def crear_app() -> Flask:
    """Crea y configura una instancia de la aplicación Flask.

    Esta fábrica se encarga de:
    1.  Crear la instancia de Flask, apuntando a las carpetas del frontend.
    2.  Establecer la clave secreta para la seguridad de las sesiones.
    3.  Registrar todos los Blueprints que contienen las rutas de la aplicación.

    Returns:
        Flask: La instancia de la aplicación, configurada y lista para usarse.
    """
    # 1. Creación de la instancia de la aplicación.
    # Se configuran las carpetas de plantillas y estáticos para que apunten
    # directamente al directorio del frontend.
    app = Flask(
        __name__,
        static_folder="../frontend/static",
        template_folder="../frontend/templates",
    )

    # 2. Configuración de la clave secreta.
    # Esencial para la seguridad de las sesiones y los mensajes flash.
    app.secret_key = config.FLASK_SECRET_KEY

    # 3. Registro de todas las rutas (Blueprints) de la aplicación.
    registrar_rutas(app)

    return app