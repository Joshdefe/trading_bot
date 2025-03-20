def evaluate_signal(indicators):
    """
    Evalúa la señal de trading en base a indicadores técnicos simples.
    Regla básica:
      - Si el RSI es menor a 30: señal de COMPRA (BUY).
      - Si el RSI es mayor a 70: señal de VENTA (SELL).
      - En cualquier otro caso: mantener (HOLD).
    
    Parámetros:
      indicators (dict): Diccionario que contiene los indicadores, por ejemplo:
         {
            'rsi': 67.5,
            'sma_20': ...,
            'sma_50': ...,
            ...
         }
    
    Retorna:
      str: "BUY", "SELL" o "HOLD"
    """
    rsi = indicators.get('rsi')
    
    if rsi is None:
        return "HOLD"
    
    if rsi < 30:
        return "BUY"
    elif rsi > 70:
        return "SELL"
    else:
        return "HOLD"
