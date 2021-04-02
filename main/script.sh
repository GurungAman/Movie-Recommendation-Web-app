import pandas as pd
from django.contrib.auth.models import User
from .models import UserRating, Movie
from django.db import models


movies = pd.read_csv("movies.csv", header=0, encoding="Latin1")
ratings = pd.read_csv("ratings.csv", header=0)

for row in range(len(movies)):
    Movie.objects.create(
        movieId = movies.iloc[row]['movieId'],
        title = movies.iloc[row]['title'],
        imdbId = movies.iloc[row]['imdbId']
        )



for row in range(len(df.userId.unique())):
    user = User.objects.create_user(
        username = 'user_id',
        password = 'dummy_pw'
    )
    user.save()


for row in range(len(ratings)):
    UserRating.objects.create(
        user_id = User.objects.get(username = ratings.iloc[row]['user_id']).id,
        movie_id = Movie.objects.get(movieId = ratings.iloc[row]['movieId']).movieId,
        rating = df.iloc[row]['rating']
    )

def check_imdbId(imdbId):
    imdbId = str(imdbId)
    x = 7 * str(0)
    new_imdbId = x + imdbId
    new_imdbId = new_imdbId[-7:]
    return "tt" + new_imdbId

for values in range(len(Movie.objects.all())):
    movies = Movie.objects.filter(movieId=values)
    if movies.exists()==True:
        movies = Movie.objects.get(movieId=values)
        movies.imdbId = check_imdbId(int(common.loc[common['movieId'] == values].imdbId.iloc[0]))
        movies.save()
    else:
        pass

