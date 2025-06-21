from flask import Flask
from config import FLASK_SECRET_KEY
from backend.rutas import registrar_rutas

def crear_app():
    """
    Crea y configura la instancia de la aplicación Flask.
    Este es el patrón de 'Application Factory'.
    """
    app = Flask(
        __name__,
        static_folder="../frontend/static",
        template_folder="../frontend/templates",
    )

    # Configura la clave secreta, necesaria para mensajes flash
    app.secret_key = FLASK_SECRET_KEY

    # Registra todos los blueprints (rutas) de la aplicación
    registrar_rutas(app)

    return app