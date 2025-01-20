# Real Time Movie-Recommendation-System
Overview
The Professional Movie Recommendation System is a web application built with Streamlit that provides personalized movie recommendations. By integrating with the TMDB API, it offers genre-based suggestions and tracks user search history to refine recommendations over time.

Features
Movie Search: Enter a movie name to receive recommendations.

Recommendations: Get suggestions based on the searched movie and your viewing history.

Search History: Saves recent searches in an Excel file for personalized recommendations.

Professional UI: Dark-themed interface with well-structured layouts for movie details.

Genre-Based Suggestions: Leverages genre overlap from search history to improve recommendations.

Installation
Clone the repository or download the code.

Ensure you have Python 3.7 or later installed.

Install the required libraries:

pip install streamlit requests pandas openpyxl rapidfuzz
Run the application:

streamlit run app.py
Usage
Launch the app by running the command above.

Enter a movie name in the input field.

Click the Get Recommendations button to see:

Similar movies.

Additional recommendations based on your past searches and genres.

View search history stored in movie_search_history.xlsx for further insights.

Technical Details
Libraries Used
Streamlit: For building the web interface.

Requests: To fetch data from the TMDB API.

RapidFuzz: For fuzzy string matching in movie names.

Pandas: For managing search history and data processing.

OpenPyXL: For Excel file handling.

API Integration
TMDB API Key: Replace the placeholder in the code with your TMDB API key.

Endpoints Used:

Fetch genres: /genre/movie/list

Search movies: /search/movie

Get recommendations: /movie/{movie_id}/recommendations
