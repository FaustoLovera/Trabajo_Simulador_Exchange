from flask import Flask, render_template, jsonify
from api_cotizaciones import obtener_datos_criptos_coingecko
from tabla_cotizaciones import obtener_tabla_criptos
from compra_y_venta import cargar_billetera, trading as vista_trading

app = Flask(
    __name__,
    static_folder='../frontend/static',
    template_folder='../frontend/templates'
)

app.secret_key = "clave_segura_para_flash"

def estado_actual():
    return cargar_billetera()

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

@app.route("/trading", methods=["GET", "POST"])
def trading():
    return vista_trading()

@app.route('/estado')
def estado():
    return jsonify(estado_actual())

@app.route("/billetera")
def billetera():
    estado = estado_actual()
    return render_template("billetera.html", estado=estado)

if __name__ == "__main__":
    app.run(debug=True)
