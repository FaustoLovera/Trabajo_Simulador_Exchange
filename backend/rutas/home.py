from flask import Blueprint, render_template

bp = Blueprint("home", __name__)

@bp.route("/")
def index():
    """
    Sirve el esqueleto de la página principal. 
    La carga y actualización de datos se maneja en el frontend.
    """
    return render_template("index.html")