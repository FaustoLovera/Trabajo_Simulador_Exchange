from flask import Flask
from config import FLASK_SECRET_KEY
from formateo_decimales import registrar_filtros

def crear_app():
    app = Flask(
        __name__,
        static_folder="../frontend/static",
        template_folder="../frontend/templates",
    )

    app.secret_key = FLASK_SECRET_KEY

    # Registrar filtros personalizados
    registrar_filtros(app)

    return app
