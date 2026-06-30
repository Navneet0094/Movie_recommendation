# # from wsgiref import headers

# import streamlit as st
# import pickle
# import pandas as pd 
# import requests

# movies_list = pickle.load(open('movies.pkl','rb'))
# similarity = pickle.load(open('similarity.pkl','rb'))
# movies = movies_list['title'].values

# def fetch_poster(movie_id):
#     url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
#     headers = {
#         "accept": "application/json",
#         "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2NTVkNjYxMmQwOTZhM2U4MzhmZGYwNzkwNDliMmQyNiIsIm5iZiI6MTc4MjU2NzE2MS42NDYwMDAxLCJzdWIiOiI2YTNmZDBmOWY0ZjVlNjBlNWRjZjA2NDciLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.XIRzc_voBTVvQ1w1S_rxnvlACFjO3G6zuvh37Mlu9N4"
#     }
#     response = requests.get(url, headers=headers)
#     data = response.json()
#     poster_path = data['poster_path']
#     full_path = "https://image.tmdb.org/t/p/w500/" + poster_path        
#     return full_path

# def recommend(movie):
#     movie_index = movies_list[movies_list['title'] == movie].index[0]
#     distances = similarity[movie_index]
#     movie_list = sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:6]
#     recommended_movies = []
#     recommended_movie_posters = []
#     for i in movie_list:
#         movie_id = movies_list.iloc[i[0]].movie_id
       
#         recommended_movies.append(movies_list.iloc[i[0]].title)
#         # fetch poster 
#         recommended_movie_posters.append(fetch_poster(movie_id))
        
#     return recommended_movies,recommended_movie_posters

# st.title('Movie Recommendation System')
# selected_movie = st.selectbox(
#     "Select a movie from the dropdown to view the recommended movies",
#     movies
# )

# if st.button("Recommend"):
# #     recommended_movies = recommend(selected_movie)
# #     for i in recommended_movies:
# #         st.write(i)
#     names,posters = recommend(selected_movie)
#     col1, col2, col3, col4, col5 = st.columns(5)
#     with col1:
#         st.text(names[0])
#         st.image(posters[0])
#     with col2:
#         st.text(names[1])
#         st.image(posters[1])

#     with col3:
#         st.text(names[2])
#         st.image(posters[2])

#     with col4:
#         st.text(names[3])
#         st.image(posters[3])

#     with col5:
#         st.text(names[4])
#         st.image(posters[4])

import streamlit as st
import pickle
import pandas as pd
import requests
import time

movies_list = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = movies_list['title'].values

API_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2NTVkNjYxMmQwOTZhM2U4MzhmZGYwNzkwNDliMmQyNiIsIm5iZiI6MTc4MjU2NzE2MS42NDYwMDAxLCJzdWIiOiI2YTNmZDBmOWY0ZjVlNjBlNWRjZjA2NDciLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.XIRzc_voBTVvQ1w1S_rxnvlACFjO3G6zuvh37Mlu9N4"

REQ_HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_TOKEN}"
}

def fetch_poster(movie_id, retries=3):
    # Primary: /images endpoint with language=en,null for maximum coverage
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/images?include_image_language=en,null"
    
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=REQ_HEADERS, timeout=10)
            data = response.json()
            posters = data.get('posters', [])

            if posters:
                # Pick the highest voted poster
                best_poster = max(posters, key=lambda x: x.get('vote_average', 0))
                return "https://image.tmdb.org/t/p/w500/" + best_poster['file_path']
            else:
                # Fallback: try the basic movie details endpoint
                fallback_url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
                fallback_response = requests.get(fallback_url, headers=REQ_HEADERS, timeout=10)
                fallback_data = fallback_response.json()
                poster_path = fallback_data.get('poster_path')
                if poster_path:
                    return "https://image.tmdb.org/t/p/w500/" + poster_path
                else:
                    return None

        except requests.exceptions.ConnectionError:
            if attempt < retries - 1:
                time.sleep(2)
            else:
                return None
        except Exception as e:
            st.warning(f"Could not fetch poster for movie ID {movie_id}: {e}")
            return None

def recommend(movie):
    movie_index = movies_list[movies_list['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_movie_posters = []
    
    for i in movie_list:
        movie_id = movies_list.iloc[i[0]].movie_id
        recommended_movies.append(movies_list.iloc[i[0]].title)
        recommended_movie_posters.append(None)
        # recommended_movie_posters.append(fetch_poster(movie_id))
    
    return recommended_movies, recommended_movie_posters

# ─── UI ────────────────────────────────────────────────────────────────────────

st.title('🎬 Movie Recommendation System')

selected_movie = st.selectbox(
    "Select a movie from the dropdown to view the recommended movies",
    movies
)

if st.button("Recommend"):
    with st.spinner("Fetching recommendations..."):
        names, posters = recommend(selected_movie)

    st.subheader("Top 5 Recommendations:")
    col1, col2, col3, col4, col5 = st.columns(5)

    for col, name, poster in zip([col1, col2, col3, col4, col5], names, posters):
        with col:
            st.text(name)
            if poster:
                st.image(poster)
            else:
                st.write("🎬 No poster available")