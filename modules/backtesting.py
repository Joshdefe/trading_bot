import pandas as pd
import numpy as np
import datetime
import ta
from modules.evaluation import evaluate_signal
from modules.risk_management import calculate_trade_quantity
from modules.logger import log_info

def run_backtesting():
    # Parámetros iniciales
    starting_balance = 2000
    balance = starting_balance
    trade_risk_percentage = 0.15
    active_trade = None
    trade_history = []

    # Cargar datos históricos desde el CSV
    try:
        df = pd.read_csv("historical_data.csv", parse_dates=["timestamp"])
    except Exception as e:
        log_info("Error al cargar datos históricos: " + str(e))
        return

    # Asegurarse de que los datos estén ordenados por timestamp
    df.sort_values("timestamp", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Iterar sobre cada fila para simular el paso del tiempo
    for index in range(len(df)):
        row = df.iloc[index]
        
        # Solo calcular indicadores si tenemos suficientes datos (por ejemplo, ventana de 14 para RSI)
        if index < 14:
            continue
        
        # Calcular RSI usando el paquete ta (utilizando los últimos 15 datos)
        df_subset = df.iloc[index-14:index+1]
        rsi = ta.momentum.RSIIndicator(df_subset['close'], window=14).rsi().iloc[-1]

        # Construir un diccionario de indicadores (otros indicadores se pueden agregar)
        indicators = {
            'rsi': rsi,
            'sma_20': df_subset['close'].rolling(window=20).mean().iloc[-1] if len(df_subset) >= 20 else np.nan,
            'sma_50': np.nan,
            'macd': 0,          # Para simplificar, no se calcula en este ejemplo
            'bb_upper': 0,
            'bb_lower': 0,
            'volumen': row['volume'],
            'volatilidad_5min': 0,
            'symbol': "TEST"
        }
        
        # Evaluar la señal (BUY, SELL o HOLD) usando el módulo de evaluación
        decision = evaluate_signal(indicators)
        
        # Lógica simple:
        # - Si no tenemos un trade activo y la señal es BUY, abrimos un trade.
        # - Si tenemos un trade activo y la señal es SELL, cerramos el trade.
        price = row['close']
        timestamp = row['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        
        if active_trade is None and decision == "BUY":
            # Abrir trade
            quantity = calculate_trade_quantity(balance, trade_risk_percentage, price)
            if quantity > 0:
                active_trade = {
                    'open_price': price,
                    'quantity': quantity,
                    'timestamp_open': timestamp
                }
                log_info(f"[{timestamp}] Trade abierto a {price:.2f} con cantidad {quantity:.4f}")
        
        elif active_trade is not None and (decision == "SELL" or index == len(df) - 1):
            # Cerrar trade
            open_price = active_trade['open_price']
            outcome_percentage = (price - open_price) / open_price
            profit = open_price * active_trade['quantity'] * outcome_percentage
            balance += profit  # Actualizamos el balance
            log_info(f"[{timestamp}] Trade cerrado a {price:.2f}: Ganancia/Pérdida = {profit:.2f}, Nuevo balance = {balance:.2f}")
            
            # Registrar en el historial
            trade_history.append({
                'timestamp_open': active_trade['timestamp_open'],
                'timestamp_close': timestamp,
                'open_price': open_price,
                'close_price': price,
                'quantity': active_trade['quantity'],
                'profit': profit,
                'balance_after': balance
            })
            active_trade = None

    log_info(f"Backtesting finalizado. Balance final: {balance:.2f}")
    print(f"Backtesting finalizado. Balance final: {balance:.2f}")
    return trade_history

if __name__ == "__main__":
    run_backtesting()
