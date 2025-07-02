"""Punto Central de Registro de Rutas (Blueprints).

Este paquete organiza todas las rutas de la aplicación en módulos desacoplados
utilizando el patrón de Blueprints de Flask. Este archivo `__init__.py` actúa
como el registrador central:

1.  **Importa** cada Blueprint desde su respectivo módulo de vistas.
2.  **Proporciona** una única función `registrar_rutas` que es llamada por la
    fábrica de la aplicación (`crear_app`) para vincular todas las rutas a la
    instancia de Flask.

Este enfoque promueve la modularidad y facilita el mantenimiento del código.
"""

from .home import bp as home_bp
from .trading_vista import bp as trading_bp
from .billetera_vista import bp as billetera_bp
from .api_externa import bp as api_externa_bp
from .api_vista import bp as api_vista_bp


def registrar_rutas(app):
    """Registra todos los Blueprints en la instancia de la aplicación Flask.

    Esta función centraliza el proceso de registro, haciendo que la inicialización
    de la aplicación sea limpia y predecible. Cada Blueprint encapsula un
    conjunto de rutas relacionadas con una funcionalidad específica.

    Args:
        app: La instancia principal de la aplicación Flask.

    Side Effects:
        Modifica el objeto `app` al registrarle los siguientes Blueprints:
        - `home_bp`: Rutas generales y de renderizado de páginas principales.
        - `trading_bp`: Endpoints para la lógica de operaciones de trading.
        - `billetera_bp`: Endpoints para la visualización de la billetera.
        - `api_externa_bp`: Endpoints que exponen datos de APIs externas.
        - `api_vista_bp`: Endpoints RESTful para el consumo de datos del frontend.
    """
    app.register_blueprint(home_bp)
    app.register_blueprint(trading_bp)
    app.register_blueprint(billetera_bp)
    app.register_blueprint(api_externa_bp)
    app.register_blueprint(api_vista_bp)
