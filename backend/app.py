import json
from flask import render_template
from backend.servicios.api_cotizaciones import obtener_datos_criptos_coingecko
from backend import crear_app

app = crear_app()

@app.route("/")
def index():
    resultado = obtener_datos_criptos_coingecko()
    print("👉 Finalizó la obtención de datos.")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
