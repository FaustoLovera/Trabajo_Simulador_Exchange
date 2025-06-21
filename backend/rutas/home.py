"""
Define la ruta principal (landing page) de la aplicación.

Este módulo es responsable de servir la página de inicio (index.html),
que actúa como el punto de entrada para los usuarios.
"""

from flask import Blueprint, render_template

bp = Blueprint("home", __name__)


@bp.route("/")
def index():
    """
    Renderiza la página de inicio de la aplicación.

    Esta ruta sirve el archivo `index.html`, que es el esqueleto principal
    de la interfaz. El contenido dinámico, como las cotizaciones, se carga
    posteriormente de forma asíncrona mediante JavaScript.

    Returns:
        Response: El contenido HTML renderizado de la página de inicio.
    """
    return render_template("index.html")