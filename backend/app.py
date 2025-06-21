"""
Punto de entrada para ejecutar la aplicación Flask en modo de desarrollo.

Este script importa la 'Application Factory' (`crear_app`), la utiliza para
crear una instancia de la aplicación y, si se ejecuta directamente, inicia
el servidor de desarrollo de Flask.

Para iniciar la aplicación, ejecuta el siguiente comando desde el directorio raíz
del proyecto:
    python -m backend.app
"""

from flask import Flask
from . import crear_app

# Se crea la instancia global de la aplicación llamando a la factory.
app: Flask = crear_app()

# El siguiente bloque se ejecuta solo si el script es llamado directamente
# por el intérprete de Python (por ejemplo, `python -m backend.app`).
if __name__ == "__main__":
    # Inicia el servidor de desarrollo de Flask.
    # `debug=True` activa el modo de depuración, que proporciona un depurador
    # interactivo y recarga automáticamente el servidor al detectar cambios.
    app.run(debug=True)