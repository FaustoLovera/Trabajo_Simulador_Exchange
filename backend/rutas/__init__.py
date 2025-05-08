from .home import bp as home_bp
from .trading_vista import bp as trading_bp
from .billetera_vista import bp as billetera_bp
from .api_externa import bp as api_ruta_bp

def registrar_rutas(app):
    app.register_blueprint(home_bp)
    app.register_blueprint(trading_bp)
    app.register_blueprint(billetera_bp)
    app.register_blueprint(api_ruta_bp)