# run.py

from backend import crear_app

# Crear la instancia de la aplicación Flask utilizando la factory.
app = crear_app()

if __name__ == '__main__':
    # Ejecutar la aplicación.
    # El host '0.0.0.0' hace que el servidor sea accesible desde otras máquinas en la misma red.
    # El modo de depuración se activa para facilitar el desarrollo.
    app.run(host='0.0.0.0', port=5001, debug=True)
