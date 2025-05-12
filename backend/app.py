from flask import render_template
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko
from . import crear_app
from flasgger import Swagger

app = crear_app()
swagger = Swagger(app)

# http://localhost:5000/apidocs
# Para ver la documentacion interactiva

if __name__ == "__main__":
    app.run(debug=True)
