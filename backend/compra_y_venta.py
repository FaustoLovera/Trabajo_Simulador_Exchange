from api_cotizaciones import obtener_datos_criptos_coingecko

# Estado ficticio del sistema
saldo_usd = 10000.0
cartera = {}

def obtener_cripto_por_ticker(ticker):
    datos_criptos = obtener_datos_criptos_coingecko()

    # Verificamos que sea una lista
    if not isinstance(datos_criptos, list):
        print("❌ Se recibió un formato inválido desde CoinGecko.")
        return None

    for cripto in datos_criptos:
        if cripto['ticker'].upper() == ticker.upper():
            return cripto

    return None

def comprar_cripto(ticker, monto_usd):
    global saldo_usd, cartera
    cripto = obtener_cripto_por_ticker(ticker)

    if not cripto:
        return {"error": "Cripto no encontrada"}

    if monto_usd > saldo_usd:
        return {"error": "Fondos insuficientes"}

    cantidad = monto_usd / cripto["precio_usd"]
    cartera[ticker.upper()] = cartera.get(ticker.upper(), 0) + cantidad
    saldo_usd -= monto_usd
    
    print(cartera)
    print (saldo_usd)

    return {
        True, f"✅ Compraste {cantidad:.6f} {ticker.upper()} por ${monto_usd:.2f}"
    }


def vender_cripto(ticker, monto_usd):
    global saldo_usd, cartera
    ticker = ticker.upper()

    cripto = obtener_cripto_por_ticker(ticker)
    if not cripto:
        return False, "Cripto no encontrada"

    cantidad_disponible = cartera.get(ticker, 0)
    precio = cripto["precio_usd"]
    cantidad_a_vender = monto_usd / precio

    if cantidad_disponible < cantidad_a_vender:
        return False, "No tenés suficiente cantidad para vender"

    cartera[ticker] -= cantidad_a_vender
    if cartera[ticker] <= 0:
        del cartera[ticker]

    saldo_usd += monto_usd

    print(cartera)
    print (saldo_usd)

    return True, f"✅ Vendiste {cantidad_a_vender:.6f} {ticker} por ${monto_usd:.2f}"



def estado_actual():
    return {
        "saldo_usd": saldo_usd,
        "cartera": cartera
    }
