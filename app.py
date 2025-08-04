import streamlit as st
import pickle
import pandas as pd
import requests
import gdown
import os

from tenacity import retry, stop_after_attempt, wait_random_exponential

# --- Download similarity.pkl from Google Drive ---
file_id = '176E5D3ij_oVl9tWNh6GEGgL1ZMH4QMQL'  # <-- Replace with your actual file ID
url = f'https://drive.google.com/uc?id={file_id}'
output = 'similarity_new.pkl'

# Download only if not already present
if not os.path.exists(output):
    st.info("Downloading similarity matrix from Google Drive...")
    gdown.download(url, output, quiet=False)

# --- Load movie data and similarity matrix ---
movies = pickle.load(open('movies_new.pkl', 'rb'))
similarity = pickle.load(open('similarity_new.pkl', 'rb'))

# --- TMDB API key ---
API_KEY = st.secrets["tmdb"]["api_key"]


@retry(stop=stop_after_attempt(3), wait=wait_random_exponential(multiplier=1, max=4))
def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    )
    data = response.json()
    poster_path = data.get('poster_path', '')
    full_path = "https://image.tmdb.org/t/p/w185/" + poster_path
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        try:
            poster = fetch_poster(movie_id)
        except Exception:
            poster = "https://via.placeholder.com/185x278.png?text=No+Image"
        recommended_posters.append(poster)

    return recommended_movies, recommended_posters

# --- Streamlit UI ---
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox("Select a movie to get recommendations", movies['title'].values)

if st.button('Show Recommendations'):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i],use_container_width=True)
