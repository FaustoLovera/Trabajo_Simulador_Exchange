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

if __name__ == "__main__":
    app.run(debug=True)