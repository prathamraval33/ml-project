import requests
import pandas as pd
import time

# Replace TMDB_API_KEY with your actual API key
API_KEY = 'TMDB_API_KEY'
base_url = "https://api.themoviedb.org/3"

movie_list = []

for page in range(1, 501):  # 500 pages * 20 movies = 10,000 movies
    print(f"Fetching page {page}")
    url = f"{base_url}/discover/movie?api_key={API_KEY}&language=en-US&sort_by=popularity.desc&page={page}"
    response = requests.get(url)
    data = response.json()

    for movie in data['results']:
        movie_id = movie['id']
        details = requests.get(f"{base_url}/movie/{movie_id}?api_key={API_KEY}").json()
        credits = requests.get(f"{base_url}/movie/{movie_id}/credits?api_key={API_KEY}").json()

        movie_list.append({
            'id': movie_id,
            'title': details.get('title'),
            'budget': details.get('budget'),
            'revenue': details.get('revenue'),
            'genres': [g['name'] for g in details.get('genres', [])],
            'runtime': details.get('runtime'),
            'release_date': details.get('release_date'),
            'production_companies': [c['name'] for c in details.get('production_companies', [])],
            'production_countries': [c['name'] for c in details.get('production_countries', [])],
            'cast': [c['name'] for c in credits.get('cast', [])[:5]],  # top 5 cast
            'director': next((crew['name'] for crew in credits.get('crew', []) if crew['job'] == 'Director'), None),
            'vote_average': details.get('vote_average'),
            'vote_count': details.get('vote_count'),
            'popularity': details.get('popularity'),
            'original_language': details.get('original_language')
        })

    time.sleep(0.25)

# Save to CSV
df = pd.DataFrame(movie_list)
df.to_csv("dataset_1_collected_data.csv", index=False)
print("Data saved")
