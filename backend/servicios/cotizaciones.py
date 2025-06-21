from flask import render_template
from backend.acceso_datos.datos_cotizaciones import cargar_datos_cotizaciones

# Las funciones 'envolver_variacion_coloreada' y 'formatear_numero' ya no son necesarias aquí.
# Podrían moverse a un módulo de utilidades si se usan en otro lugar, o eliminarse si no.
# Para esta solución, las eliminamos de este archivo para simplificarlo.

def renderizar_fragmento_tabla():
    cotizaciones_crudas = cargar_datos_cotizaciones()
    return render_template("fragmento_tabla.html", cotizaciones=cotizaciones_crudas)