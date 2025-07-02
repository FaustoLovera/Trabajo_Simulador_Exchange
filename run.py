"""
Punto de entrada para ejecutar la aplicación Flask del simulador de exchange.

Este script es el responsable de instanciar y correr la aplicación web. Utiliza la
función factory `crear_app` del paquete `backend` para construir la instancia de Flask,
lo que permite una configuración flexible y desacoplada.

Para iniciar el servidor de desarrollo, ejecute este archivo desde la terminal:
$ python run.py
"""

from backend import crear_app

# Se crea la instancia de la aplicación Flask llamando a la factory.
# Este patrón de diseño (Application Factory) es una buena práctica en Flask porque
# permite crear múltiples instancias de la app con diferentes configuraciones
# (por ejemplo, una para desarrollo y otra para pruebas) y evita importaciones circulares.
app = crear_app()

# El bloque `if __name__ == '__main__'` asegura que el código dentro de él solo se
# ejecute cuando el script es invocado directamente por el intérprete de Python.
# Esto previene que el servidor se inicie si el script es importado desde otro módulo.
if __name__ == '__main__':
    # Inicia el servidor de desarrollo integrado de Flask.
    app.run(
        host='0.0.0.0',  # Hace que el servidor sea visible y accesible desde cualquier dispositivo en la misma red.
        port=5001,       # Especifica el puerto en el que la aplicación escuchará las peticiones.
        debug=True       # Activa el modo de depuración, que proporciona recarga automática y un depurador interactivo.
    )
