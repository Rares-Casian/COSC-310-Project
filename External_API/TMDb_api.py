import requests
import os
import json
from dotenv import load_dotenv
import uuid

load_dotenv()
API_TOKEN = os.getenv("TMDB_API_TOKEN")


def getTrending():
    url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=1"

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {API_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    data = response.json()

    return data

def save_tmdb_json(response_json, filename="backend/data/tmdb_data.json"):
    """
    Saves TMDb API response to a JSON file with nice formatting.
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(response_json, f, indent=4, ensure_ascii=False)
    print(f"Data saved to {filename}")

def transform_tmdb_to_files():
    # Load original TMDb JSON
    with open("backend/data/tmdb_data.json", "r", encoding="utf-8") as f:
        tmdb_data = json.load(f)

    # Load existing mapping if it exists
    mapping_file = "movies_transformed/tmdb_uuid_map.json"
    if os.path.exists(mapping_file):
        with open(mapping_file, "r", encoding="utf-8") as f:
            tmdb_uuid_map = json.load(f)
    else:
        tmdb_uuid_map = {}

    # Create output folder if it doesn't exist
    output_dir = "movies_transformed"
    os.makedirs(output_dir, exist_ok=True)

    for movie in tmdb_data.get("results", []):
        tmdb_id = str(movie.get("id"))

        # Reuse UUID if already mapped, otherwise generate new
        if tmdb_id in tmdb_uuid_map:
            movie_id = tmdb_uuid_map[tmdb_id]
        else:
            movie_id = str(uuid.uuid4())
            tmdb_uuid_map[tmdb_id] = movie_id

        transformed = {
            "movie_id": movie_id,
            "title": movie.get("title"),
            "imdb_rating": movie.get("vote_average"),
            "meta_score": None,
            "genres": movie.get("genre_ids", []),
            "directors": [],
            "release_date": movie.get("release_date"),
            "duration": None,
            "description": movie.get("overview"),
            "main_stars": [],
            "total_user_reviews": None,
            "total_critic_reviews": None,
            "total_rating_count": movie.get("vote_count"),
            "source_folder": movie.get("title")
        }

        # Save individual movie JSON
        filename = os.path.join(output_dir, f"{movie_id}.json")
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(transformed, f, indent=4, ensure_ascii=False)

    # Save mapping for next runs
    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(tmdb_uuid_map, f, indent=4)

    print(f"Saved {len(tmdb_data.get('results', []))} movies to '{output_dir}' folder.")


transform_tmdb_to_files()




# Example usage:
#save_tmdb_json(data)  call from outside of this file in the actual implementation

"""
To use the api set the url to the correct end point which can be found in the documentation
set the headers to the correct values which can be found in the documentation 
 
To use it for another type of request only change the url and "accept" field leave the "Authorization" feild the same

The data returns by the api will be stores in respose which can than be used. Calling the api will have to be done outside of this file so only one function is called at a time

Delete the save_tmdb_json(data) before using 

To set the token create a .env file in the root directory where the backend folder is 
and write TMDB_API_TOKEN=INSERT TOKEN HERE 

the token is located in the note/resources channel in the discord 

DO NOT HARD CODE THE API KEY use "API_TOKEN = os.getenv("TMDB_API_TOKEN")"
the .env file is in the .gitignore so it will not be pushed to the github
"""

