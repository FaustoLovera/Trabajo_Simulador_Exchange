from flask import Flask, render_template, jsonify
import api_cotizaciones

app = Flask(
    __name__,
    static_folder='../frontend/static',
    template_folder='../frontend/templates'
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/trading")
def trading():
    return render_template("trading.html")

@app.route("/billetera")
def billetera():
    return render_template("billetera.html")

if __name__ == "__main__":
    app.run(debug=True)