import pandas as pd
import matplotlib.pyplot as plt

def plot_trade_history(csv_file="logs/trades.csv"):
    # Cargar el historial de trades desde el archivo CSV
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"Error al leer {csv_file}: {e}")
        return

    if df.empty:
        print("No hay datos en el historial de trades.")
        return

    # Convertir la columna de timestamp a datetime, si existe
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    else:
        print("La columna 'timestamp' no se encuentra en el CSV.")
        return

    # Ordenar por la fecha de los trades
    df = df.sort_values("timestamp")
    
    # Crear un gráfico de la evolución del balance después de cada trade
    plt.figure(figsize=(10, 6))
    plt.plot(df["timestamp"], df["balance_after"], marker="o", linestyle="-")
    plt.title("Evolución del Balance tras cada Trade")
    plt.xlabel("Fecha y Hora")
    plt.ylabel("Balance (USDT)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_trade_history()
