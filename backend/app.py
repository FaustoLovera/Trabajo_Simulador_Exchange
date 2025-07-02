"""
Este módulo crea una instancia global de la aplicación Flask utilizando la
'Application Factory' (`crear_app`).

Esta instancia 'app' puede ser utilizada por otras herramientas, como un servidor
WSGI (por ejemplo, Gunicorn o uWSGI), que esperan encontrar una variable de
aplicación global.

El punto de entrada principal para iniciar el servidor de desarrollo es ahora
el script `run.py` en el directorio raíz del proyecto.
"""

from flask import Flask
from . import crear_app

# Se crea la instancia global de la aplicación llamando a la factory.
app: Flask = crear_app()