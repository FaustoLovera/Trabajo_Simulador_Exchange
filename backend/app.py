import json
from flask import Flask, render_template, jsonify
from api_cotizaciones import obtener_datos_criptos_coingecko, obtener_velas_binance
from tabla_cotizaciones import obtener_tabla_criptos
from compra_y_venta import cargar_billetera, trading as vista_trading
from billetera import estado_actual_completo

app = Flask(
    __name__,
    static_folder="../frontend/static",
    template_folder="../frontend/templates",
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
    obtener_velas_binance()
    return vista_trading()


@app.route("/api/historial")
def api_historial():
    try:
        with open("datos/historial_operaciones.json", "r") as f:
            historial = json.load(f)
        return jsonify(historial)
    except Exception as e:
        print("Error al cargar historial:", e)
        return jsonify({"error": "No se pudo cargar el historial"}), 500


@app.route("/estado")
def estado():
    return jsonify(estado_actual())


@app.route("/billetera")
def billetera():
    estado = estado_actual()
    return render_template("billetera.html", estado=estado)


@app.route("/api/billetera")
def api_billetera():
    estado = estado_actual_completo()
    return jsonify(estado)


@app.route("/api/velas")
def obtener_datos_velas():
    try:
        with open("datos/datos_velas.json", "r") as archivo:
            datos = json.load(archivo)
        return jsonify(datos)
    except Exception as e:
        print("❌ Error leyendo datos_velas.json:", e)
        return jsonify({"error": "No se pudo leer el archivo"}), 500


if __name__ == "__main__":
    app.run(debug=True)
