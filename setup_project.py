import os

# Definir la estructura de carpetas y archivos
files = {
    "modules/__init__.py": "",
    "modules/trading.py": '''import pandas as pd
import numpy as np
import joblib
import time
import requests
from binance.client import Client
from dotenv import load_dotenv
import os
import ta
from modules.logger import log_info, log_error

# Cargar variables de entorno
load_dotenv("key.env")
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Conectar a Binance (testnet para pruebas)
client = Client(API_KEY, API_SECRET, testnet=True)

# Intentar cargar el modelo entrenado
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
    if modelo_ml is None:
        return "BUY"
    
    try:
        features_df = pd.DataFrame([indicators]).drop(columns=['symbol'])
        pred = modelo_ml.predict(features_df)
        return "BUY" if pred[0] == 1 else "HOLD"
    except Exception as e:
        log_error(f"Error en la evaluación del trade {symbol}: {e}")
        return "BUY"

def registrar_trade(symbol, action, indicators, resultado):
    try:
        trade_data = {
            'symbol': symbol,
            'accion': action,
            'rsi': indicators.get('rsi'),
            'sma_20': indicators.get('sma_20'),
            'sma_50': indicators.get('sma_50'),
            'macd': indicators.get('macd'),
            'bb_upper': indicators.get('bb_upper'),
            'bb_lower': indicators.get('bb_lower'),
            'volumen': indicators.get('volumen'),
            'volatilidad_5min': indicators.get('volatilidad_5min'),
            'resultado': resultado
        }
        df = pd.DataFrame([trade_data])
        log_file = "logs/qlearning_data.csv"
        header = not os.path.exists(log_file)
        df.to_csv(log_file, mode='a', header=header, index=False)
        log_info(f"Trade registrado: {trade_data}")
    except Exception as e:
        log_error(f"Error al registrar trade para {symbol}: {e}")

def run_trading():
    START_BALANCE = 2000
    TRADE_RISK_PERCENTAGE = 0.15
    balance = START_BALANCE
    profit_total = 0
    total_trades = 0

    log_info("Módulo de Trading iniciado.")
    while True:
        try:
            tickers = client.get_ticker()
            df_tickers = pd.DataFrame(tickers)
            df_tickers['volatility'] = abs(df_tickers['priceChangePercent'].astype(float))
            top_pairs = df_tickers.nlargest(30, 'volatility')['symbol'].tolist()[:10]

            for symbol in top_pairs:
                indicators = get_technical_indicators(symbol)
                if indicators is None:
                    continue
                decision = evaluate_trade(symbol, indicators)
                if decision == "BUY":
                    price = float(client.get_symbol_ticker(symbol=symbol)['price'])
                    quantity = (START_BALANCE * TRADE_RISK_PERCENTAGE) / price
                    balance -= price * quantity
                    registrar_trade(symbol, "BUY", indicators, resultado=0)
                    log_info(f"Compra ejecutada para {symbol} a {price:.6f} por cantidad {quantity:.4f}")

            log_info(f"Estado: Saldo={balance:.2f} USDT")
            time.sleep(60)
        except Exception as e:
            log_error(f"Error en módulo de Trading: {e}")
            time.sleep(60)
''',
    "modules/telegram_bot.py": '''from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
from dotenv import load_dotenv
from modules.logger import log_info

# Cargar variables de entorno
load_dotenv("key.env")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hola, soy tu bot de inversiones. ¿En qué puedo ayudarte?')
    log_info("Comando /start recibido.")

def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)
    log_info(f"Echo: {update.message.text}")

def run_telegram_bot():
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Comando start
    dispatcher.add_handler(CommandHandler("start", start))
    # Puedes añadir más comandos aquí

    # Inicia el bot
    updater.start_polling()
    log_info("Telegram Bot iniciado.")
    updater.idle()
''',
    "modules/logger.py": '''import logging
import os

# Configurar carpeta de logs
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configurar el logging
logging.basicConfig(
    filename="logs/bot_inversiones.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_info(message):
    logging.info(message)

def log_error(message):
    logging.error(message)
''',
    "main.py": '''import threading
from modules.telegram_bot import run_telegram_bot
from modules.trading import run_trading
from modules.logger import log_info

def main():
    log_info("Iniciando Bot de Inversiones con IA...")
    
    # Ejecutar Telegram en un hilo aparte
    telegram_thread = threading.Thread(target=run_telegram_bot)
    telegram_thread.start()

    # Ejecutar módulo de Trading
    run_trading()

if __name__ == "__main__":
    main()
''',
    "key.env": '''BINANCE_API_KEY=tu_binance_api_key_aqui
BINANCE_API_SECRET=tu_binance_api_secret_aqui
TELEGRAM_BOT_TOKEN=tu_telegram_bot_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
''',
    "requirements.txt": '''python-telegram-bot
binance
ta
pandas
numpy
python-dotenv
joblib
'''
}

# Función para crear directorios y archivos
def create_files(file_dict):
    for filepath, content in file_dict.items():
        # Asegurarse de que el directorio existe
        dirpath = os.path.dirname(filepath)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath)
            print(f"Directorio creado: {dirpath}")
        # Escribir el contenido en el archivo
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            print(f"Archivo creado: {filepath}")

# Crear el directorio de logs si no existe
if not os.path.exists("logs"):
    os.makedirs("logs")
    print("Directorio creado: logs")

# Crear los archivos definidos
create_files(files)

print("Estructura de proyecto creada exitosamente.")
