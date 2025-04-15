from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from api_cotizaciones import obtener_datos_criptos_coingecko
from tabla_cotizaciones import obtener_tabla_criptos
from compra_y_venta import comprar_cripto, vender_cripto, cargar_billetera, obtener_estado

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
    criptos = obtener_datos_criptos_coingecko()
    estado = obtener_estado()  # Obtener el estado actual

    if request.method == "POST":
        ticker = request.form["ticker"]
        accion = request.form["accion"]
        monto = float(request.form["monto"])

        if accion == "comprar":
            exito, mensaje = comprar_cripto(ticker, monto)
        elif accion == "vender":
            exito, mensaje = vender_cripto(ticker, monto)
        else:
            exito, mensaje = False, "Acción inválida."

        flash(mensaje, "success" if exito else "danger")
        return redirect(url_for("trading"))

    return render_template("trading.html", criptos=criptos, estado=estado)  # Pasamos el estado a la plantilla

@app.route('/estado')
def estado():
    return jsonify(estado_actual())

@app.route("/billetera")
def billetera():
    estado = estado_actual()
    return render_template("billetera.html", estado=estado)

if __name__ == "__main__":
    app.run(debug=True)
