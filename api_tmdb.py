# api_tmdb.py

import requests
import time

class TMDbAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"

    def get_top_rated_movies(self, page=1):
        url = f"{self.base_url}/movie/top_rated"
        params = {
            "api_key": self.api_key, 
            "language": "pt-BR",
            "page": page
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Erro {response.status_code}: {response.text}")
            return None
        data = response.json()
        return data

    def get_movie_details(self, movie_id):
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            "api_key": self.api_key,  
            "language": "pt-BR",
            "append_to_response": "credits"
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Erro {response.status_code}: {response.text}")
            return None
        data = response.json()
        return data

    def rate_limit(self):
        time.sleep(0.25)  
