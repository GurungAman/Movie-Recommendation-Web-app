"""RecommendationWebApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name="homepage"),
    path('register/', views.register, name="register"),
    path('log_in/', views.log_in , name="log_in"),
    path('log_out/', views.log_out , name="log_out"),
    path('movie/<int:pk>/', views.details, name="details"),
    path('recommendations/', views.recommend_movies, name='recommend'),
    path('list/', views.movie_list, name='movie_list'),
    path('watch_list/', views.movies_rated_by_user, name='watch_list'),
    path('movie/<int:pk>/delete', views.delete_rating, name='delete'),
    path('profile/', views.user_profile, name='profile'),
]



