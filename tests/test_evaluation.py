import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.evaluation import evaluate_signal

def test_evaluate_signal():
    # Caso 1: RSI bajo (señal de compra)
    indicators_buy = {'rsi': 25}
    print("Con RSI 25:", evaluate_signal(indicators_buy))  # Esperado: BUY

    # Caso 2: RSI alto (señal de venta)
    indicators_sell = {'rsi': 75}
    print("Con RSI 75:", evaluate_signal(indicators_sell))  # Esperado: SELL

    # Caso 3: RSI intermedio (mantener)
    indicators_hold = {'rsi': 50}
    print("Con RSI 50:", evaluate_signal(indicators_hold))  # Esperado: HOLD

if __name__ == "__main__":
    test_evaluate_signal()
