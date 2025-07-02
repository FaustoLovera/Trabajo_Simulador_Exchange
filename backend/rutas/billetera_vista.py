"""Blueprint para las Rutas de la Sección de Billetera y Portafolio.

Este módulo actúa como un **Controlador** que gestiona la petición HTTP
para renderizar la página principal de la billetera del usuario.

Responsabilidad:
- **Renderizado de Página**: Sirve la página principal `billetera.html`.

Los datos para la página se cargan de forma asíncrona a través de los
endpoints definidos en `api_vista.py`.
"""

from flask import Blueprint, render_template

# Define el Blueprint con el prefijo de URL `/billetera`.
bp = Blueprint("billetera", __name__, url_prefix="/billetera")


@bp.route("/") # Ruta -> /billetera/
def mostrar_billetera():
    """
    Renderiza la página principal de la billetera.

    Esta ruta sirve el archivo `billetera.html`, que actúa como el contenedor
    principal para la interfaz de la billetera. Los datos se cargan de forma
    asíncrona a través de llamadas a la API desde JavaScript.

    Returns:
        Response: El contenido HTML renderizado de la página de la billetera.
    """
    return render_template("billetera.html")