from flask import Flask
from config import FLASK_SECRET_KEY
from backend.utils.formateo_decimales import registrar_filtros
from backend.rutas import registrar_rutas


def crear_app():
    app = Flask(
        __name__,
        static_folder="../frontend/static",
        template_folder="../frontend/templates",
    )

    app.secret_key = FLASK_SECRET_KEY

    registrar_filtros(app)
    registrar_rutas(app)

    return app
