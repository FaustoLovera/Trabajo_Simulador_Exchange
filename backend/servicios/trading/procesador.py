# backend/servicios/trading/procesador.py

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Tuple

from backend.acceso_datos.datos_billetera import cargar_billetera, guardar_billetera
from backend.acceso_datos.datos_cotizaciones import obtener_precio, cargar_datos_cotizaciones
from backend.acceso_datos.datos_historial import guardar_en_historial
from backend.acceso_datos.datos_comisiones import registrar_comision
from backend.acceso_datos.datos_ordenes import agregar_orden_pendiente
from backend.utils.utilidades_numericas import a_decimal, cuantizar_cripto, cuantizar_usd, formato_cantidad_cripto, formato_cantidad_usd
from config import TASA_COMISION

# --- Funciones Auxiliares (privadas a este módulo) ---

def _validar_saldo_disponible(billetera: dict, moneda_origen: str, cantidad_requerida: Decimal) -> Tuple[bool, str | None]:
    activo = billetera.get(moneda_origen)
    if not activo:
        return False, f"❌ No posees {moneda_origen} en tu billetera."
    saldo_disponible = a_decimal(activo['saldos'].get("disponible"))
    if cantidad_requerida > saldo_disponible:
        return False, f"❌ Saldo insuficiente. Tienes {formato_cantidad_cripto(saldo_disponible)} {moneda_origen} disponibles, pero se requieren {formato_cantidad_cripto(cantidad_requerida)}."
    return True, None

def _crear_activo_si_no_existe(billetera: dict, ticker: str):
    if ticker not in billetera:
        info_criptos = {c['ticker']: c for c in cargar_datos_cotizaciones()}
        info_nueva_moneda = info_criptos.get(ticker, {"nombre": ticker})
        billetera[ticker] = {"nombre": info_nueva_moneda.get("nombre", ticker), "saldos": {"disponible": a_decimal("0"), "reservado": a_decimal("0")}}

def _ejecutar_orden_mercado(moneda_origen: str, moneda_destino: str, monto_form: Decimal, modo_ingreso: str, accion: str) -> Tuple[bool, str]:
    precio_origen_usdt = obtener_precio(moneda_origen)
    precio_destino_usdt = obtener_precio(moneda_destino)
    if not all([precio_origen_usdt, precio_destino_usdt]) or precio_origen_usdt.is_zero() or precio_destino_usdt.is_zero():
        return False, "❌ No se pudo obtener la cotización para realizar el swap."

    if accion == 'comprar':
        cantidad_destino_bruta = monto_form if modo_ingreso == 'monto' else (monto_form * precio_origen_usdt) / precio_destino_usdt
        cantidad_origen_bruta = (cantidad_destino_bruta * precio_destino_usdt) / precio_origen_usdt
    else:
        cantidad_origen_bruta = monto_form
        cantidad_destino_bruta = (cantidad_origen_bruta * precio_origen_usdt) / precio_destino_usdt

    billetera = cargar_billetera()
    exito_validacion, mensaje_error = _validar_saldo_disponible(billetera, moneda_origen, cantidad_origen_bruta)
    if not exito_validacion: return False, mensaje_error

    cantidad_comision = cantidad_origen_bruta * TASA_COMISION
    registrar_comision(moneda_origen, cantidad_comision, cantidad_comision * precio_origen_usdt)

    cantidad_origen_neta_swap = cantidad_origen_bruta - cantidad_comision
    cantidad_destino_neta = (cantidad_origen_neta_swap * precio_origen_usdt) / precio_destino_usdt

    billetera[moneda_origen]["saldos"]["disponible"] -= cantidad_origen_bruta
    _crear_activo_si_no_existe(billetera, moneda_destino)
    billetera[moneda_destino]["saldos"]["disponible"] += cantidad_destino_neta
    guardar_billetera(billetera)

    guardar_en_historial("compra" if moneda_origen == "USDT" else "venta" if moneda_destino == "USDT" else "intercambio", moneda_origen, cantidad_origen_neta_swap, moneda_destino, cantidad_destino_neta, cantidad_origen_neta_swap * precio_origen_usdt)
    
    mensaje_html = f"""
    <div style='text-align: left; font-size: 1.1rem;'><b>Operación de Mercado Exitosa</b><hr style='margin: 4px 0; border-color: #555;'>
    <span>Recibiste: <strong style='color: #1FB371;'>{formato_cantidad_cripto(cantidad_destino_neta)} {moneda_destino}</strong></span><br>
    <span>Pagaste: <strong style='color: #FFA500;'>{formato_cantidad_cripto(cantidad_origen_bruta)} {moneda_origen}</strong></span><br>
    <span style='font-size: 0.8rem; color: #999;'>Comisión: {formato_cantidad_cripto(cantidad_comision)} {moneda_origen}</span></div>
    """
    return True, mensaje_html

def _crear_orden_pendiente(moneda_origen: str, moneda_destino: str, monto_form: Decimal, precio_disparo: Decimal, tipo_orden: str, accion: str) -> Tuple[bool, str]:
    billetera = cargar_billetera()
    if accion == 'comprar':
        cantidad_destino_orden, monto_a_reservar = monto_form, monto_form * precio_disparo
        moneda_a_reservar, cantidad_origen_orden = moneda_origen, monto_a_reservar
    else:
        cantidad_origen_orden, monto_a_reservar = monto_form, monto_form
        moneda_a_reservar, cantidad_destino_orden = moneda_origen, monto_form * precio_disparo

    exito_validacion, mensaje_error = _validar_saldo_disponible(billetera, moneda_a_reservar, monto_a_reservar)
    if not exito_validacion: return False, mensaje_error

    billetera[moneda_a_reservar]["saldos"]["disponible"] -= monto_a_reservar
    billetera[moneda_a_reservar]["saldos"]["reservado"] += monto_a_reservar
    guardar_billetera(billetera)

    nueva_orden = {
        "id_orden": str(uuid.uuid4()), "timestamp_creacion": datetime.now().isoformat(),
        "tipo_orden": tipo_orden, "accion": accion, "par": f"{moneda_destino}/{moneda_origen}",
        "moneda_origen": moneda_origen, "moneda_destino": moneda_destino,
        "cantidad_origen": str(cuantizar_cripto(cantidad_origen_orden)),
        "cantidad_destino": str(cuantizar_cripto(cantidad_destino_orden)),
        "precio_disparo": str(cuantizar_usd(precio_disparo)), "estado": "pendiente"
    }
    agregar_orden_pendiente(nueva_orden)
    
    accion_texto, cantidad_mostrada, ticker_mostrado = ("Compra", cantidad_destino_orden, moneda_destino) if accion == 'comprar' else ("Venta", cantidad_origen_orden, moneda_origen)
    mensaje_html = f"""
    <div style='text-align: left; font-size: 0.9rem;'><b>Orden {tipo_orden.capitalize()} Creada</b><hr style='margin: 4px 0; border-color: #555;'>
    <span>Acción: <strong>{accion_texto} de {formato_cantidad_cripto(cantidad_mostrada)} {ticker_mostrado}</strong></span><br>
    <span>Precio Disparo: <strong>{formato_cantidad_usd(precio_disparo)}</strong></span><br>
    <span style='font-size: 0.8rem; color: #999;'>Los fondos han sido reservados.</span></div>
    """
    return True, mensaje_html

# --- Punto de Entrada Público ---

def procesar_operacion_trading(formulario: dict) -> Tuple[bool, str]:
    """Valida la entrada del formulario y la despacha al procesador de órdenes correcto."""
    try:
        ticker_principal = formulario["ticker"].upper()
        accion = formulario["accion"]
        monto_form = a_decimal(formulario["monto"])
        tipo_orden = formulario.get("tipo-orden", "market").lower()
    except KeyError as e:
        return False, f"❌ Error en los datos del formulario, falta el campo: {e}"

    if monto_form <= a_decimal(0): return False, "❌ El monto debe ser un número positivo."

    moneda_origen, moneda_destino = (formulario.get("moneda-pago", "USDT").upper(), ticker_principal) if accion == "comprar" else (ticker_principal, formulario.get("moneda-recibir", "USDT").upper())
    if moneda_origen == moneda_destino: return False, "❌ La moneda de origen y destino no pueden ser la misma."

    if tipo_orden == "market":
        modo_ingreso = formulario.get("modo-ingreso", "monto")
        if accion == 'vender' and modo_ingreso == 'total': return False, "❌ Al vender, debe ingresar la cantidad en modo 'Cantidad (Cripto)'."
        return _ejecutar_orden_mercado(moneda_origen, moneda_destino, monto_form, modo_ingreso, accion)
    
    elif tipo_orden in ["limit", "stop-loss"]:
        precio_disparo = a_decimal(formulario.get("precio_disparo"))
        if precio_disparo <= a_decimal(0): return False, "❌ Se requiere un precio de disparo válido y positivo."
        return _crear_orden_pendiente(moneda_origen, moneda_destino, monto_form, precio_disparo, tipo_orden, accion)
    
    return False, f"❌ Tipo de orden desconocido: '{tipo_orden}'."