from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd


# Десериализуем SVD модель из файла
svd_opt = joblib.load('models/svd_opt.joblib')
# Загружаем данные для расчетов
movie_to_genres = joblib.load('models/movie_to_genres.joblib')
user_genre_avg = pd.read_csv('models/user_genre_avg.csv')
ratings = pd.read_csv('models/ratings.csv')
movies = pd.read_csv('models/movies.csv')
global_avg = 3.513013093920591

def content_based_predict(user_id, movie_id):
    genres = movie_to_genres.get(movie_id, [])
    if not genres:
        return global_avg
    try:
        user_avg = user_genre_avg.loc[user_id]
    except KeyError:
        return global_avg
    valid_ratings = [user_avg[g] for g in genres if g in user_avg and not np.isnan(user_avg[g])]
    return np.mean(valid_ratings) if valid_ratings else global_avg

def recommendations_for_user(user_id, top_n=10, min_rating=3.5, exclude_watched=True):
  try:
    # Определяем фильмы, которые пользователь уже смотрел
    watched_movies = ratings[ratings['userId'] == user_id]['movieId'].to_list() if exclude_watched else []

    # Формируем список фильмов, которе пользователь не видел
    movies_to_recommend = [m for m in movies['movieId'].unique() if m not in watched_movies]

    predictions = []
    for movie_id in movies_to_recommend:
      # Применяем гибридную модель для расчета рейтинга фильма
      # i = 0.2 дала лучший результат на тесте
      pred_rating = svd_opt.predict(user_id, movie_id).est * (1 - 0.2) + content_based_predict(user_id, movie_id) * 0.2
      if pred_rating and pred_rating >= min_rating:
        predictions.append({
            'movieId': movie_id,
            'prediction_rating': pred_rating
        })

    recommendations = sorted(predictions, key=lambda x: x['prediction_rating'], reverse=True)

    return recommendations[:top_n]
  except Exception as e:
    print(f"Ошибка предсказания для пользователя {user_id}: {e}")
    return None


app = Flask(__name__)

@app.route('/recommendations', methods=['POST'])
def predict():
    user_id = request.json.get('user_id')
    rec = recommendations_for_user(user_id)
    rec_df = pd.DataFrame(rec)
    rec_df = rec_df.merge(movies[['movieId', 'title']], on='movieId', how='left')
    rec_dict = rec_df.to_dict()

    return  jsonify({'recommendation': rec_dict})

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)
