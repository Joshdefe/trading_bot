import threading
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
