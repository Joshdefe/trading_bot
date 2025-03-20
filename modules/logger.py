import logging
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
