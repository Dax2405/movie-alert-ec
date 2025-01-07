import requests
import re
from dotenv import load_dotenv
import os
import time
import logging
import threading


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

url = os.getenv("URL")
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
movie_name = os.getenv("MOVIE_NAME")
movie_name_en = os.getenv("MOVIE_NAME_EN")


def get_data():
    while True:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error al obtener los datos: {response.status_code}")
                time.sleep(10)
        
        except Exception as e:
            logger.error(f"Error al obtener los datos: {e}")
            time.sleep(10)


def get_movies():
    
    response = get_data()
    try:
        movies = []
        for movie in response[0]['detail']:
            movies.append(movie['title'])
        
        return movies
    except Exception as e:
        logger.error(f"Error al obtener las películas: {e}")
        return []
        
    

def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
        data = {
            "chat_id": telegram_chat_id,
            "text": text
        }
        response = requests.post(url, data=data)
        if response.status_code==200:
            logger.info("Mensaje enviado correctamente")
        else:
            logger.error(f"Error al enviar el mensaje: {response.json()}")
    except Exception as e:
        logger.error(f"Error al enviar el mensaje(petición): {e}")
    
    
def verify_movie():
    
    print(movie_name)
    print(movie_name_en)    
    movies = get_movies()
    pattern_es = re.compile(re.escape(movie_name), re.IGNORECASE)
    pattern_en = re.compile(re.escape(movie_name_en), re.IGNORECASE)
    for movie in movies:
        if pattern_es.search(movie) or pattern_en.search(movie):
            send_telegram_message(f"Hola! tu película {movie_name} está en cartelera en Supercines 6 de diciembre")
            return True
    return False




def check_movie_periodically():
    counter = 0

    while True:
        if counter%100 == 0:
            try:
                send_telegram_message("info: The script is alive")
            except Exception as e:
                logger.error(f"Error al enviar el correo de inicio de verificación: {e}")

        try:
            if verify_movie():
                logger.info(f"La película '{movie_name}' está disponible.")
            else:
                logger.info(f"La película '{movie_name}' no está disponible.")
        except Exception as e:
            logger.error(f"Error al verificar la película: {e}")
        counter += 10
        time.sleep(300)

threading.Thread(target=check_movie_periodically, daemon=True).start()

while True:
    time.sleep(1)