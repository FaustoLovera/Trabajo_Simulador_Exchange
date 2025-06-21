from flask import Flask
from backend.rutas import registrar_rutas


def crear_app():
    app = Flask(
        __name__,
        static_folder="../frontend/static",
        template_folder="../frontend/templates",
    )


    return app
