"""
This module is responsible for downloading the data from the TMDB API.
run only once to download the data from the TMDB API and save it to the data directory. using 'python src/ingestion/data_downloader.py' 
"""

import os
import requests
from dotenv import load_dotenv
from src.utils import get_config

load_dotenv()
config = get_config()

TMDB_KEY = os.getenv("TMDB_KEY")
TMDB_URL = os.getenv("TMDB_URL")


def get_movie_details(movie_id):
    url = f"{TMDB_URL}/movie/{movie_id}?api_key={TMDB_KEY}&language=en-US"
    response = requests.get(url)
    return response.json()


def get_movie_credits(movie_id):
    url = f"{TMDB_URL}/movie/{movie_id}/credits?api_key={TMDB_KEY}"
    response = requests.get(url)
    data = response.json()

    actors = [cast['name'] for cast in data.get('cast',[])[:5]]  # Get top 5 actors if mant actors per movie are available
    director = next(
        (crew['name'] for crew in data.get('crew', []) if crew['job'] == 'Director'),
        None
    )

    return actors, director



def get_popular_movies(page=1):
    url = f"{TMDB_URL}/movie/popular?api_key={TMDB_KEY}&language=en-US&page={page}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: on page {page}: {response.status_code}")
        return []

    data = response.json()

    movies_data = []

    for movie in data['results']:
        movie_id = movie['id']

        details = get_movie_details(movie_id) or {}
        actors, director = get_movie_credits(movie_id)

        genres = [g['name'] for g in details.get('genres', [])]

        movie_info = {
            "title": movie['title'],
            "year": movie['release_date'][:4] if movie['release_date'] else None,
            "rating": movie['vote_average'],
            "description": details.get('overview', ''),
            "actors": ", ".join(actors),
            "genres": ", ".join(genres),
            "director": director
        }

        movies_data.append(movie_info)

    return movies_data


import pandas as pd
import time

output_path = config.data_path
output_path.mkdir(parents=True, exist_ok=True)

all_movies = []
for page in range(1, 101):
    all_movies.extend(get_popular_movies(page))
    time.sleep(0.25) # Sleep for 0.25 seconds to avoid rate limiting or got blocked by the API

df = pd.DataFrame(all_movies)
df.drop_duplicates(subset="title", inplace=True)
df.to_csv(output_path / "movies.csv", index=False)

print(f"Saved to {output_path / 'movies.csv'}")