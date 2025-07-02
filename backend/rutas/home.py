"""Blueprint para las Rutas Generales y la Página Principal.

Este módulo define las rutas estáticas y de renderizado principal de la aplicación.
Su responsabilidad se limita a servir el 'cascarón' o 'shell' de la aplicación
(el archivo `index.html`), que luego se encarga de cargar todo el contenido
dinámico de forma asíncrona a través de llamadas a otros endpoints de la API.
"""

from flask import Blueprint, render_template

# Define el Blueprint para este módulo. El nombre 'home' se usa para la resolución
# de URLs y la organización interna de Flask.
bp = Blueprint("home", __name__)


@bp.route("/")
def index():
    """Renderiza la página de inicio de la aplicación (el 'shell').

    Esta vista sirve el archivo `index.html`, que actúa como el punto de entrada
    de la Single-Page Application (SPA). Este HTML contiene la estructura base,
    y el resto del contenido (cotizaciones, billetera, etc.) es cargado y
    renderizado por el código JavaScript del lado del cliente.

    Returns:
        La respuesta HTTP con el contenido de `index.html` renderizado.
    """
    return render_template("index.html")