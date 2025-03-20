import sys
import os
import pprint

# Ajustar el path para poder importar módulos desde la raíz
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.trading import get_technical_indicators, evaluate_trade

def test_get_indicators():
    # Usa un símbolo válido en Binance Testnet, por ejemplo "BTCUSDT"
    symbol = "BTCUSDT"
    indicators = get_technical_indicators(symbol)
    if indicators:
        print("Indicadores obtenidos:")
        pprint.pprint(indicators)
    else:
        print("No se pudieron obtener indicadores.")

def test_evaluate_trade():
    # Usar el símbolo en el formato que Binance espera, por ejemplo "BTCUSDT"
    symbol = "BTCUSDT"
    indicators = get_technical_indicators(symbol)
    if indicators is None:
        print(f"No se pudieron obtener indicadores para {symbol}")
    else:
        print("Indicadores obtenidos:")
        pprint.pprint(indicators)
        decision = evaluate_trade(symbol, indicators)
        print(f"Decisión para {symbol}: {decision}")

if __name__ == "__main__":
    print("Ejecutando test_get_indicators:")
    test_get_indicators()
    print("\nEjecutando test_evaluate_trade:")
    test_evaluate_trade()
