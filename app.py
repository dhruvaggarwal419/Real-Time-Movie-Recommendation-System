import streamlit as st
import requests
from rapidfuzz import process
import pandas as pd
from datetime import datetime
import os

# Set the title and custom CSS for the app
st.set_page_config(page_title="Professional Movie Recommendation System", layout="wide")
st.markdown(
    """
    <style>
    body {
        background-color: #000000;
    }
    .stApp {
        background-color: #000000;
    }
    .stTitle {
        color: #ffffff !important;
    }
    .stMarkdown h3 {
        color: #ffffff !important;
    }
    .stMarkdown p {
        color: #cccccc !important;
    }
    .stButton > button {
        background-color: #1e1e1e;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        border: 1px solid #444;
    }
    .stButton > button:hover {
        background-color: #333333;
    }
    .movie-container {
        display: flex;
        align-items: flex-start;
        margin-bottom: 20px;
        border: 1px solid #444;
        border-radius: 10px;
        padding: 15px;
        background-color: #1e1e1e;
    }
    .movie-poster {
        margin-right: 20px;
        max-width: 150px;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(255, 255, 255, 0.1);
    }
    .movie-details {
        max-width: 800px;
    }
    .movie-details h3 {
        color: #ffffff;
    }
    .movie-details p {
        color: #cccccc;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎥 Professional Movie Recommendation System")

# TMDB API configuration
TMDB_API_KEY = "Your API Key"
TMDB_API_URL = "https://api.themoviedb.org/3"

# Input field for movie name
movie_name = st.text_input("Enter the name of the movie:")

# Fetch genres (cached for efficiency)
@st.cache_data
def fetch_genres():
    genres_url = f"{TMDB_API_URL}/genre/movie/list?api_key={TMDB_API_KEY}"
    response = requests.get(genres_url)
    if response.status_code == 200:
        genres_data = response.json().get("genres", [])
        return {genre['id']: genre['name'] for genre in genres_data}
    return {}

genres_mapping = fetch_genres()

# Fetch recommendations from TMDB API
def fetch_recommendations(movie_id):
    recommendations_url = f"{TMDB_API_URL}/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}"
    response = requests.get(recommendations_url)
    if response.status_code == 200:
        return response.json().get("results", [])
    return []

# Save search history to Excel
def save_search_history_to_excel(search_data):
    file_path = "movie_search_history.xlsx"
    if not os.path.exists(file_path):
        df = pd.DataFrame(search_data, columns=["Search Term", "Genres", "Timestamp"])
        df.to_excel(file_path, index=False, engine='openpyxl')
    else:
        df = pd.read_excel(file_path, engine='openpyxl')
        new_data = pd.DataFrame(search_data, columns=["Search Term", "Genres", "Timestamp"])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(file_path, index=False, engine='openpyxl')

# Get genre-based recommendations from search history
def get_genre_based_recommendations(current_genre_ids):
    file_path = "movie_search_history.xlsx"
    if os.path.exists(file_path):
        df = pd.read_excel(file_path, engine='openpyxl')
        if not df.empty:
            # Extract genres from the last 5 searches
            last_searches = df.tail(5)
            history_genres = sum(last_searches["Genres"].apply(eval).tolist(), []) 
            
            # Find common genres
            common_genres = set(current_genre_ids).intersection(set(history_genres)) 
            
            # Fetch movies based on common genres
            if common_genres:
                genre_id = list(common_genres)[0]  # Select one genre for simplicity
                genre_url = f"{TMDB_API_URL}/discover/movie?api_key={TMDB_API_KEY}&with_genres={genre_id}"
                response = requests.get(genre_url)
                if response.status_code == 200:
                    return response.json().get("results", [])
    return []

# Search for movies based on the user's input
if st.button("Get Recommendations"):
    if movie_name:
        st.write("Fetching data...")
        
        # Search for movies matching the input
        search_url = f"{TMDB_API_URL}/search/movie?api_key={TMDB_API_KEY}&query={movie_name}"
        response = requests.get(search_url)
        
        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                # Use fuzzy matching for better title suggestions
                movie_titles = [result["title"] for result in data["results"]]
                matches = process.extract(movie_name, movie_titles, limit=8)
                
                # Include the "Did you mean" movies in recommendations
                recommendations = []
                for match, score, index in matches:
                    recommendations.append(data["results"][index])
                
                # Fetch additional recommendations for the best match
                best_match_id = recommendations[0]["id"]
                additional_recommendations = fetch_recommendations(best_match_id)
                recommendations.extend(additional_recommendations)
                
                # Get 2 recommendations based on search history and common genres
                best_match_genre_ids = recommendations[0].get("genre_ids", [])
                genre_recommendations = get_genre_based_recommendations(best_match_genre_ids)
                recommendations.extend(genre_recommendations[:2])  # Append genre-based recommendations
                
                # Save the search history to Excel
                save_search_history_to_excel([
                    {
                        "Search Term": movie_name,
                        "Genres": best_match_genre_ids,
                        "Timestamp": datetime.now().isoformat()
                    }
                ])
                
                # Display recommendations with a professional UI
                st.subheader("🌟 Recommended Movies")
                for rec_movie in recommendations[:8]:  # Limit to 8
                    poster_path = rec_movie.get("poster_path")
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                    movie_title = rec_movie.get("title", "Unknown Title")
                    release_date = rec_movie.get("release_date", "Unknown Release Date")
                    overview = rec_movie.get("overview", "No overview available.")
                    genre_ids = rec_movie.get("genre_ids", [])
                    genres = [genres_mapping.get(genre_id, "Unknown") for genre_id in genre_ids]
                    
                    # Display movie details in a structured format
                    st.markdown(
                        f"""
                        <div class="movie-container">
                            <img src="{poster_url}" class="movie-poster" alt="{movie_title}">
                            <div class="movie-details">
                                <h3>{movie_title}</h3>
                                <p><strong>Release Date:</strong> {release_date}</p>
                                <p><strong>Genres:</strong> {', '.join(genres)}</p>
                                <p><strong>Overview:</strong> {overview}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                
                # Now display details of the genre-based recommendations at the end (if any)
                for rec_movie in genre_recommendations[:2]:  # Display only the genre-based recommendations
                    poster_path = rec_movie.get("poster_path")
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                    movie_title = rec_movie.get("title", "Unknown Title")
                    release_date = rec_movie.get("release_date", "Unknown Release Date")
                    overview = rec_movie.get("overview", "No overview available.")
                    genre_ids = rec_movie.get("genre_ids", [])
                    genres = [genres_mapping.get(genre_id, "Unknown") for genre_id in genre_ids]
                    
                    # Display movie details in a structured format
                    st.markdown(
                        f"""
                        <div class="movie-container">
                            <img src="{poster_url}" class="movie-poster" alt="{movie_title}">
                            <div class="movie-details">
                                <h3>{movie_title}</h3>
                                <p><strong>Release Date:</strong> {release_date}</p>
                                <p><strong>Genres:</strong> {', '.join(genres)}</p>
                                <p><strong>Overview:</strong> {overview}</p>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.write("No movies found. Please refine your input.")
        else:
            st.write("Failed to fetch data from TMDB API.")
    else:
        st.write("Please enter a movie name.")
