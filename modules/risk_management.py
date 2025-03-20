def calculate_trade_quantity(balance, trade_risk_percentage, price):
    """
    Calcula la cantidad de activos a comprar basándose en el balance disponible,
    el porcentaje de riesgo por trade y el precio actual.
    """
    try:
        quantity = (balance * trade_risk_percentage) / price
        return quantity
    except Exception as e:
        print(f"Error calculando la cantidad de trade: {e}")
        return 0

def update_balance(balance, price, quantity, trade_outcome_percentage):
    """
    Actualiza el balance tras una operación.
    
    Parámetros:
      - balance: Balance actual.
      - price: Precio de ejecución del trade.
      - quantity: Cantidad comprada.
      - trade_outcome_percentage: Porcentaje de ganancia (positivo) o pérdida (negativo)
    
    Retorna el balance actualizado.
    """
    # Calcula el cambio en valor. Por ejemplo, si trade_outcome_percentage es 0.05 (5% de ganancia)
    # se suma al balance, o si es -0.03 (3% de pérdida) se resta.
    change = price * quantity * trade_outcome_percentage
    return balance + change

def can_open_new_trade(active_trades, max_open_trades):
    """
    Verifica si se puede abrir un nuevo trade comparando las operaciones abiertas
    con el máximo permitido.
    """
    return len(active_trades) < max_open_trades
