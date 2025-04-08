from flask import Flask, render_template, jsonify
from api_cotizaciones import obtener_datos_criptos_coingecko
from tabla_cotizaciones import obtener_tabla_criptos

app = Flask(
    __name__,
    static_folder='../frontend/static',
    template_folder='../frontend/templates'
)

@app.route("/")
def index():
    resultado = obtener_datos_criptos_coingecko()
    print("👉 Finalizó la obtención de datos.")
    return render_template("index.html")

@app.route("/actualizar")
def actualizar():
    datos = obtener_datos_criptos_coingecko()
    return jsonify({"estado": "ok", "cantidad": len(datos)})

@app.route("/datos_tabla")
def datos_tabla():
    return jsonify(obtener_tabla_criptos())

@app.route("/trading")
def trading():
    return render_template("trading.html")

@app.route("/billetera")
def billetera():
    return render_template("billetera.html")

if __name__ == "__main__":
    app.run(debug=True)