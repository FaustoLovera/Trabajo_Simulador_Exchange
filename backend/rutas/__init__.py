"""
Inicializa el paquete de rutas y registra todos los Blueprints de la aplicación.

Este archivo importa los Blueprints definidos en los diferentes módulos de vistas
(home, trading, billetera, etc.) y proporciona una función centralizada `registrar_rutas`
para vincularlos a la instancia principal de la aplicación Flask.
"""

from .home import bp as home_bp
from .trading_vista import bp as trading_bp
from .billetera_vista import bp as billetera_bp
from .api_externa import bp as api_ruta_bp


def registrar_rutas(app):
    """
    Registra todos los Blueprints de la aplicación en la instancia de Flask.

    Args:
        app (Flask): La instancia principal de la aplicación Flask a la que se
                     registrarán los Blueprints.

    Side Effects:
        Modifica el objeto `app` registrando las rutas definidas en los Blueprints.
    """
    app.register_blueprint(home_bp)
    app.register_blueprint(trading_bp)
    app.register_blueprint(billetera_bp)
    app.register_blueprint(api_ruta_bp)
