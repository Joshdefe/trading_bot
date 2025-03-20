import os
import pandas as pd
import datetime

LOG_FILE = "logs/trades.csv"

def init_trade_log():
    """
    Inicializa el archivo de registro de trades. Si no existe, lo crea con encabezados.
    """
    if not os.path.exists("logs"):
        os.makedirs("logs")
    if not os.path.exists(LOG_FILE):
        df = pd.DataFrame(columns=["timestamp", "symbol", "action", "open_price", "close_price", "quantity", "result", "balance_after"])
        df.to_csv(LOG_FILE, index=False)

def register_trade(timestamp, symbol, action, open_price, close_price, quantity, result, balance_after):
    """
    Registra los detalles de un trade en un archivo CSV.
    
    Parámetros:
      - timestamp: Fecha y hora de la operación.
      - symbol: Símbolo del activo.
      - action: Tipo de operación ("OPEN" o "CLOSE").
      - open_price: Precio de apertura del trade.
      - close_price: Precio de cierre del trade (puede ser None si aún está abierto).
      - quantity: Cantidad del activo operado.
      - result: Ganancia o pérdida obtenida en la operación.
      - balance_after: Balance después de la operación.
    """
    trade_data = {
        "timestamp": timestamp,
        "symbol": symbol,
        "action": action,
        "open_price": open_price,
        "close_price": close_price,
        "quantity": quantity,
        "result": result,
        "balance_after": balance_after
    }
    df = pd.DataFrame([trade_data])
    df.to_csv(LOG_FILE, mode='a', header=False, index=False)
