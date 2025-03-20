import pandas as pd
import numpy as np
import joblib
import time
import requests
from binance.client import Client
from dotenv import load_dotenv
import os
import ta
from modules.logger import log_info, log_error
from modules.evaluation import evaluate_signal
from modules.risk_management import calculate_trade_quantity, can_open_new_trade
from modules.evaluation import evaluate_signal
from modules.sentiment import sentiment_for_asset

# Cargar variables de entorno
load_dotenv("key.env")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Conectar a Binance (Testnet para pruebas)
client = Client(API_KEY, API_SECRET, testnet=True)

# Intentar cargar el modelo entrenado (opcional)
try:
    modelo_ml = joblib.load('modelo_qlearning_v2.pkl')
    log_info("Modelo Q-Learning v2 cargado exitosamente.")
except FileNotFoundError:
    log_error("No se encontró el modelo. Ejecutando sin predicciones.")
    modelo_ml = None

def get_technical_indicators(symbol):
    try:
        klines = client.get_klines(symbol=symbol, interval='1m', limit=50)
        df = pd.DataFrame(klines, columns=['time','open','high','low','close','volume','ct','qav','trades','tbb','tbq','ignore'])
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)

        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
        df['macd'] = ta.trend.MACD(df['close']).macd()
        bb = ta.volatility.BollingerBands(df['close'], window=20)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        df['volatilidad_5min'] = df['high'].rolling(window=5).max() - df['low'].rolling(window=5).min()

        df = df.dropna()
        latest_data = df.iloc[-1]

        return {
            'symbol': symbol,
            'rsi': latest_data['rsi'],
            'sma_20': df['close'].rolling(window=20).mean().iloc[-1],
            'sma_50': df['close'].rolling(window=50).mean().iloc[-1],
            'macd': latest_data['macd'],
            'bb_upper': latest_data['bb_upper'],
            'bb_lower': latest_data['bb_lower'],
            'volumen': latest_data['volume'],
            'volatilidad_5min': latest_data['volatilidad_5min']
        }
    except Exception as e:
        log_error(f"Error al obtener indicadores para {symbol}: {e}")
        return None
def evaluate_trade(symbol, indicators):
    """
    Combina la señal técnica y el análisis de sentimiento para determinar la acción.
    La función primero obtiene la señal técnica usando evaluate_signal y luego
    obtiene el sentimiento para el activo.
    
    Ejemplo simple de integración:
      - Si el sentimiento es muy negativo (por debajo de -0.3), se fuerza una señal SELL.
      - En caso contrario, se usa la señal técnica.
    """
    technical_signal = evaluate_signal(indicators)
    sentiment_score = sentiment_for_asset(symbol, page_size=3)  # Podemos usar menos noticias para mayor rapidez

    # Integración simple: si el sentimiento es negativo fuerte, forzamos SELL.
    if sentiment_score is not None and sentiment_score < -0.3:
        return "SELL"
    else:
        return technical_signal

def run_trading():
    global balance
    log_info("Módulo de Trading iniciado.")
    
    while True:
        try:
            tickers = client.get_ticker()
            df_tickers = pd.DataFrame(tickers)
            df_tickers['volatility'] = abs(df_tickers['priceChangePercent'].astype(float))
            top_pairs = df_tickers.nlargest(30, 'volatility')['symbol'].tolist()[:10]

            for symbol in top_pairs:
                if not can_open_new_trade(active_trades, MAX_OPEN_TRADES):
                    log_info("Máximo número de trades abiertos alcanzado.")
                    break

                indicators = get_technical_indicators(symbol)
                if indicators is None:
                    continue

                decision = evaluate_trade(symbol, indicators)
                log_info(f"Evaluación para {symbol}: {decision}")
                if decision == "BUY":
                    price = float(client.get_symbol_ticker(symbol=symbol)['price'])
                    quantity = calculate_trade_quantity(balance, TRADE_RISK_PERCENTAGE, price)
                    if quantity <= 0:
                        continue

                    # Simula la ejecución del trade
                    balance -= price * quantity  # Actualiza el balance al comprar
                    active_trades[symbol] = {
                        'price': price,
                        'quantity': quantity,
                        'time': time.time()
                    }
                    log_info(f"Compra ejecutada para {symbol}: Precio={price:.6f}, Cantidad={quantity:.4f}, Nuevo Balance={balance:.2f}")
            
            log_info(f"Estado del Balance: {balance:.2f} USDT")
            time.sleep(60)
        except Exception as e:
            log_error(f"Error en módulo de Trading: {e}")
            time.sleep(60)

def close_trade(symbol, current_price):
    """
    Cierra la operación abierta para el símbolo indicado usando el precio actual.
    Calcula el porcentaje de ganancia o pérdida basado en el precio de apertura y actualiza el balance.
    """
    global balance
    trade = active_trades.get(symbol)
    if not trade:
        log_info(f"No hay trade abierto para {symbol} para cerrar.")
        return

    open_price = trade['price']
    quantity = trade['quantity']
    # Calcula el porcentaje de cambio
    outcome_percentage = (current_price - open_price) / open_price

    # Actualiza el balance usando la función de gestión de riesgo
    from modules.risk_management import update_balance
    new_balance = update_balance(balance, open_price, quantity, outcome_percentage)
    profit = new_balance - balance
    balance = new_balance

    # Registra el cierre del trade
    from modules.trade_logger import register_trade
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    register_trade(timestamp, symbol, "CLOSE", open_price, current_price, quantity, profit, balance)

    # Elimina el trade de los trades activos
    del active_trades[symbol]
    log_info(f"Trade cerrado para {symbol}: Precio de cierre = {current_price:.6f}, Resultado = {profit:.2f}, Nuevo balance = {balance:.2f}")
