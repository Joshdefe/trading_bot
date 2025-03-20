import requests
from nltk.sentiment import SentimentIntensityAnalyzer
import os
from dotenv import load_dotenv

# Obtiene el directorio actual del módulo, luego sube un nivel (al directorio raíz) y carga key.env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'key.env'))

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from modules.logger import log_info, log_error

# Cargar variables de entorno
load_dotenv("key.env")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")  # Asegúrate de tener una API key de NewsAPI

# Inicializar el analizador de sentimiento de VADER
sia = SentimentIntensityAnalyzer()

def get_news(query, page_size=5):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "es",
        "pageSize": page_size,
        "apiKey": NEWS_API_KEY
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        # Agrega un print para ver la respuesta
        print("Respuesta de NewsAPI:", data)
        if data.get("status") != "ok":
            log_error("Error en la consulta de noticias: " + str(data))
            return []
        return data.get("articles", [])
    except Exception as e:
        log_error("Error al obtener noticias: " + str(e))
        return []


def analyze_sentiment(text):
    """
    Analiza el sentimiento de un texto y devuelve la puntuación.
    """
    sentiment = sia.polarity_scores(text)
    return sentiment  # Devuelve un diccionario con 'neg', 'neu', 'pos' y 'compound'

def sentiment_for_asset(asset, page_size=5):
    # Modifica el query: si asset es "BTCUSDT", usa "Bitcoin" en su lugar.
    query = asset
    if asset.upper() == "BTCUSDT":
        query = "Bitcoin"
    
    articles = get_news(query, page_size)
    if not articles:
        log_info("No se encontraron noticias para " + query)
        return None

    compound_scores = []
    for article in articles:
        content = article.get("description") or article.get("content") or ""
        if content:
            score = analyze_sentiment(content)
            compound_scores.append(score.get("compound", 0))

    if compound_scores:
        avg_sentiment = sum(compound_scores) / len(compound_scores)
        log_info(f"Sentimiento promedio para {query}: {avg_sentiment:.4f}")
        return avg_sentiment
    else:
        log_info("No se pudo calcular sentimiento para " + query)
        return None
