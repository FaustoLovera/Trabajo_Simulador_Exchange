"""Punto de entrada para servidores WSGI.

Este módulo expone la instancia global de la aplicación Flask (`app`), creada
a través de la factory `crear_app`.

Servidores de producción como Gunicorn o uWSGI utilizan esta variable `app`
para ejecutar la aplicación. Para desarrollo, se recomienda usar el script `run.py`.
"""

from flask import Flask
from . import crear_app

# Instancia global de la aplicación, utilizada por servidores WSGI.
app: Flask = crear_app()