import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from main.models import Movie, UserRating


def recommend(user):
    rating = pd.DataFrame(UserRating.objects.all().values())
    movies = pd.DataFrame(Movie.objects.all().values()) 
    Mean = rating.groupby(by='user_id', as_index=False)['rating'].mean()

    avg_rating = pd.merge(rating, Mean, on='user_id')
    avg_rating['adj_movie_rating'] = avg_rating['rating_x'] - avg_rating['rating_y']

    table = pd.pivot_table(avg_rating, values='adj_movie_rating', index='user_id', columns='movie_id')
    # table = table.apply(lambda row: row.fillna(row.mean()), axis=1)
    final_table = table.fillna(table.mean(axis=0))
    
    cosine = cosine_similarity(final_table)
    np.fill_diagonal(cosine, 0)
    similar_users = pd.DataFrame(cosine, index=final_table.index, columns=final_table.index)

    n_neighbours = 30

    top_30_neighbours = similar_users.apply(lambda x: pd.Series(x.sort_values(ascending=False).iloc[:n_neighbours].index, index=['top{}'.format(i) for i in range(1, n_neighbours + 1)]), axis=1)

    list_of_user_ids = pd.DataFrame(top_30_neighbours.loc[user].tolist(), columns=["user_id"])
    list_of_user_ids.loc[30] = user

    users_and_movies = pd.merge(pd.merge(list_of_user_ids, avg_rating, on='user_id'), movies, left_on='movie_id', right_on='movieId')
    users_and_movies = users_and_movies.pivot_table(index='user_id', columns='movie_id', values='adj_movie_rating')

    correlation_matrix = users_and_movies.corr(method='pearson', min_periods=1)
    user_corr = pd.Series([],dtype=pd.StringDtype())
    for film in users_and_movies.loc[user].dropna().index:
        corr_list = correlation_matrix[film].dropna() * users_and_movies.loc[user][film]
        user_corr = user_corr.append(corr_list)

    user_corr = user_corr.groupby(user_corr.index).sum()
    user_corr.columns = ['movie_id', 'score']

    watched_movies = []
    for i in range(len(users_and_movies.loc[user].dropna().index)):
        if users_and_movies.loc[user].dropna().index[i] in user_corr:
            watched_movies.append(users_and_movies.loc[user].dropna().index[i])

    user_corr = user_corr.drop(watched_movies)

    suggestions = []
    for i in user_corr.sort_values(ascending=False).index[:32]:
        suggestions.append(i)

    return suggestions



