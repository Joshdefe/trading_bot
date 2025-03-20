from telegram import Update
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
    # En la versión 13.7, use_context se usa para activar el modo de contexto.
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Agregar manejador para el comando /start
    dispatcher.add_handler(CommandHandler("start", start))
    # Puedes agregar más comandos aquí

    # Inicia el bot
    updater.start_polling()
    log_info("Telegram Bot iniciado.")
    updater.idle()
