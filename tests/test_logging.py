from modules.logger import log_info, log_error

def test_logs():
    log_info("Mensaje informativo de prueba.")
    log_error("Mensaje de error de prueba.")

if __name__ == "__main__":
    test_logs()
