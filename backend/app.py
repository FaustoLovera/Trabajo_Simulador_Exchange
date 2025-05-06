import json
from flask import Flask, render_template, jsonify
from api_cotizaciones import obtener_datos_criptos_coingecko, obtener_velas_binance
from tabla_cotizaciones import obtener_tabla_criptos
from compra_y_venta import cargar_billetera, trading as vista_trading
from billetera import estado_actual_completo
from config import FLASK_SECRET_KEY, HISTORIAL_PATH, VELAS_PATH

app = Flask(
    __name__,
    static_folder="../frontend/static",
    template_folder="../frontend/templates",
)

app.secret_key = FLASK_SECRET_KEY


def estado_actual():
    """
    Obtiene el estado actual de la billetera, cargando los datos almacenados 
    en el archivo correspondiente. Retorna la información de la billetera, 
    que incluye los saldos de las criptomonedas y de USDT.

    La función depende de la función `cargar_billetera()` para leer y 
    devolver los datos actuales de la billetera desde un archivo.
    """
    
    return cargar_billetera()


@app.route("/")
def index():
    """
    Obtiene los datos de criptomonedas desde la API de CoinGecko y luego 
    renderiza la plantilla HTML principal (index.html). 

    La función llama a `obtener_datos_criptos_coingecko()` para obtener la 
    información de las criptomonedas y muestra un mensaje indicando que 
    la obtención de datos ha finalizado antes de renderizar la página web.
    """
    
    resultado = obtener_datos_criptos_coingecko()
    print("👉 Finalizó la obtención de datos.")
    return render_template("index.html")


@app.route("/actualizar")
def actualizar():
    """
    Obtiene los datos más recientes de criptomonedas desde la API de CoinGecko 
    y retorna una respuesta JSON con el estado de la operación y la cantidad 
    de criptomonedas obtenidas.

    La función llama a `obtener_datos_criptos_coingecko()` para obtener los datos 
    y devuelve un objeto JSON que incluye el estado de la operación ("ok") 
    y el número de criptomonedas obtenidas.
    """
    
    datos = obtener_datos_criptos_coingecko()
    return jsonify({"estado": "ok", "cantidad": len(datos)})


@app.route("/datos_tabla")
def datos_tabla():
    """
    Obtiene los datos de criptomonedas formateados en una tabla y los retorna 
    como una respuesta JSON.

    La función llama a `obtener_tabla_criptos()` para generar la tabla de datos 
    y devuelve la tabla en formato JSON a la solicitud realizada.
    """
    
    return jsonify(obtener_tabla_criptos())


@app.route("/trading", methods=["GET", "POST"])
def trading():
    """
    Gestiona la ruta de trading, obteniendo las velas de Binance y luego 
    renderizando la vista de trading.

    La función llama a `obtener_velas_binance()` para obtener los datos de velas 
    y luego renderiza la vista de trading a través de la función `vista_trading()`, 
    permitiendo a los usuarios realizar operaciones de trading.
    """
    
    obtener_velas_binance()
    return vista_trading()


@app.route("/api/historial")
def api_historial():
    """
    Proporciona el historial de operaciones en formato JSON a través de una API.

    La función intenta cargar el historial de operaciones desde un archivo JSON. 
    Si tiene éxito, devuelve el historial como una respuesta JSON. En caso de error 
    al cargar el archivo, devuelve un mensaje de error con un código de estado 500.
    """
    
    try:
        with open(HISTORIAL_PATH, "r") as f:
            historial = json.load(f)
        return jsonify(historial)
    except Exception as e:
        print("Error al cargar historial:", e)
        return jsonify({"error": "No se pudo cargar el historial"}), 500


@app.route("/estado")
def estado():
    """
    Proporciona el estado actual de la billetera en formato JSON.

    La función obtiene el estado actual de la billetera utilizando la función 
    `estado_actual()` y lo devuelve como una respuesta JSON.
    """
    
    return jsonify(estado_actual())


@app.route("/billetera")
def billetera():
    """
    Renderiza la página de la billetera con el estado actual.

    La función obtiene el estado actual de la billetera utilizando `estado_actual()` 
    y lo pasa al template `billetera.html` para su visualización.
    """
    
    estado = estado_actual()
    return render_template("billetera.html", estado=estado)


@app.route("/api/billetera")
def api_billetera():
    """
    Proporciona el estado completo de la billetera en formato JSON.

    La función obtiene el estado completo de la billetera utilizando la función 
    `estado_actual_completo()` y lo devuelve como una respuesta JSON.
    """
    
    estado = estado_actual_completo()
    return jsonify(estado)


@app.route("/api/velas")
def obtener_datos_velas():
    """
    Obtiene los datos de las velas almacenados en el archivo de velas y los devuelve en formato JSON.

    La función lee los datos del archivo de velas, que contiene información sobre velas 
    de criptomonedas, y devuelve estos datos como una respuesta JSON. En caso de error, se maneja la 
    excepción y se retorna un mensaje de error con un código de estado 500.
    """
    
    try:
        with open(VELAS_PATH, "r") as archivo:
            datos = json.load(archivo)
        return jsonify(datos)
    except Exception as e:
        print("❌ Error leyendo datos_velas.json:", e)
        return jsonify({"error": "No se pudo leer el archivo"}), 500


if __name__ == "__main__":
    app.run(debug=True)
