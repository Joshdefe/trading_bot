import sys
import os
# Agregar el directorio raíz al path para poder importar módulos del proyecto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import modules.trading as trading
from modules.trade_logger import init_trade_log
import datetime

def test_close_trade():
    # Inicializa el registro de trades
    init_trade_log()

    # Simula la apertura de un trade
    symbol = "BTCUSDT"
    open_price = 87000.0
    quantity = 0.1  # Por ejemplo, 0.1 BTC
    
    trading.active_trades[symbol] = {
        'price': open_price,
        'quantity': quantity,
        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    print(f"Trade abierto para {symbol} a precio {open_price}, cantidad {quantity}")
    print(f"Balance antes de cerrar trade: {trading.balance:.2f} USDT")

    # Simula que el precio ha cambiado y se cierra el trade
    closing_price = 87500.0
    trading.close_trade(symbol, closing_price)

    print(f"Balance después de cerrar trade: {trading.balance:.2f} USDT")

if __name__ == "__main__":
    test_close_trade()
