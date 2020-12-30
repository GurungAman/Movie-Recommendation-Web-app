from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import RegisterUser, EditProfile
from .models import Movie, UserRating
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import Http404
from .recommendation import recommend  
from django.contrib.auth.decorators import login_required
import requests
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie


def get_movie_details(imdbId):
	url 		= "http://www.omdbapi.com/?apikey=a23d4f9a&i=" + str(imdbId) 
	response 	= requests.get(url)
	movie_data 	= response.json()
	return movie_data
	

def homepage(request):
	movies = Movie.objects.all()
	query  = request.GET.get('q')
	if query:
		movies 		= Movie.objects.filter(Q(title__icontains=query)).distinct()[:8]
		poster_path = []
		for movie in movies:
			imdbId 		= movie.imdbId
			poster_link = get_movie_details(imdbId)['Poster']
			poster_path.append(poster_link)
		movies_and_posters = zip(movies, poster_path)
		return render(request,'main/index.html', {'movies_and_posters': movies_and_posters})
	return render(request,'main/index.html')


def register(request):
	if request.method == "POST":
		form = RegisterUser(request.POST)
		if form.is_valid():
			user 		= form.save(commit=False)
			username	= form.cleaned_data['username']
			password 	= form.cleaned_data['password']

			# Another way to create user import User MOdel
			# first_name = form.cleaned_data['first_name']
			# last_name = form.cleaned_data['last_name']
			# email = form.cleaned_data['email']
			# user = User.objects.create_user(username=username, password=password, email=email,
			#                                first_name=first_name, last_name=last_name)

			user 	= user.set_password(password)
			user 	= form.save()
			login(request, user)
			messages.success(request, f'Account created for {username}!')
			return redirect("homepage")
		else:
			return render(request=request,
						  template_name="main/register.html",
						  context={"form":form})
	form = RegisterUser(auto_id=True)
	return render(request=request,
				  template_name="main/register.html",
				  context={"form": form})


@login_required(login_url='log_in')
def user_profile(request):
	if request.method == "POST":
		form = EditProfile(request.POST, instance=request.user)
		if form.is_valid():
			user 	 	= form.save(commit=False)
			username	= request.user.username
			password 	= form.cleaned_data['password']
			user 		= user.set_password(password)
			user 		= form.save()
			messages.success(request, 'Your account has been updated!')
			return redirect('homepage')
		else:
			return render(request,
				template_name="main/profile.html",
				context={"form": form})

	form = EditProfile(auto_id=True, instance=request.user)
	return render(request,
				template_name="main/profile.html",
				context={"form": form})


def log_in(request):
	if request.method == "POST":
		username 	= request.POST['username']
		password 	= request.POST['password']
		user 		= authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.info(request, f"Logged in as {username}.!")
			return redirect("homepage")
		else:
			return render(request=request,
						  template_name='main/log_in.html',
						  context={'error_message': 'Invalid Credentials.!'})

	return render(request=request,
				  template_name="main/log_in.html")
	

def movie_list(request):
	Movies 		= Movie.objects.filter().order_by('title')
	paginator 	= Paginator(Movies, 20)
	page_number = request.GET.get('page')
	page_obj	= paginator.get_page(page_number)
	movies 		= page_obj.object_list 
	poster_path = []
	for movie in movies:
		imdbId = movie.imdbId
		poster_link = get_movie_details(imdbId)['Poster']
		poster_path.append(poster_link)
	movies_and_posters = zip(movies, poster_path)
	return render(request, 
				template_name="main/list.html", 
				context={"movies_and_posters": movies_and_posters,
						"page_obj": page_obj})


def movies_rated_by_user(request):
	user 			= request.user.id
	movies_rated 	= UserRating.objects.filter(user_id=user)
	id_of_movies_rated = [movie for movies in movies_rated.values('movie_id') for _, movie in movies.items()]
	poster_path 	= [] 
	movies 			= []
	for values in id_of_movies_rated:
		movie 		= Movie.objects.get(movieId=values)
		movies.append(movie)
		imdbId 		= movie.imdbId
		poster_link = get_movie_details(imdbId)['Poster']
		poster_path.append(poster_link)
	paginator 	= Paginator(movies, 12)
	page_number = request.GET.get('page')
	page_obj	= paginator.get_page(page_number)
	movie 		= page_obj.object_list 
	paginator_poster 	= Paginator(poster_path, 12)
	page_obj_poster		= paginator_poster.get_page(page_number)
	poster 				= page_obj_poster.object_list 

	movies_and_posters = zip(movie, poster)

	return render(request,
				template_name='main/watched_list.html',
				context={"movies_and_posters": movies_and_posters,
						"page_obj": page_obj})


@login_required(login_url='log_in')
def details(request, pk):
	movies 			= Movie.objects.get(movieId=pk)
	imdbId 			= movies.imdbId
	user   			= request.user.id
	movie_details 	= get_movie_details(imdbId)

	try:
		rating = UserRating.objects.get(user_id=user,movie_id=pk)
		old_rating = rating.rating
	except:
		old_rating = 0
	if request.method == "POST":
		rate 	= request.POST['rating']
		rating 	= UserRating.objects.filter(user_id=user,movie_id=pk)
		if rating.exists():
			UserRating.objects.filter(user_id=user,movie_id=pk).update(rating=rate)
			messages.success(request,"Your Rating has been updated.")        
		else:
			UserRating.objects.create(user_id=user,movie_id=pk, rating=rate)
			messages.success(request,"Your Rating has been submited.")
			
		return render(request=request,
					template_name='main/details.html',
					context={"movies":movies,
							"movie_details": movie_details,
							"old_rating": rate})

	return render(request=request,
				  template_name='main/details.html',
				  context={"movies":movies,
				  			"movie_details": movie_details,
							"old_rating": old_rating})


@login_required(login_url='log_in')
@cache_page(60*3)
@vary_on_cookie
def recommend_movies(request):
	user 			= request.user.id
	movies 			= [] 
	poster_path 	= []
	if len(UserRating.objects.filter(user_id=user)) < 12:
		messages.info(request, "Please rate at least 12 movies to get recommendations.!")
		return redirect('movie_list')

	recommendations = recommend(user)
	for values in recommendations:
		movie 		= Movie.objects.get(movieId=values)
		imdbId 		= movie.imdbId
		poster_link = get_movie_details(imdbId)['Poster']
		movies.append(movie)
		poster_path.append(poster_link)

	movies_and_posters = zip(movies, poster_path)
	return render(request,
				template_name='main/recommendation.html',
				context={"movies_and_posters": movies_and_posters})


def delete_rating(request, pk):
	movie 	= Movie.objects.get(movieId=pk)
	user 	= request.user.id
	try:
		if request.method == "POST":
			rating = UserRating.objects.get(user_id=user, movie_id=pk)
			rating.delete()
			messages.success(request, "Rating successfully deleted.!")
			return redirect(homepage)
	except:
		messages.info(request,"You have not rated this movie yet.")
		return redirect(homepage)

	return render(request,
				template_name="main/delete_rating.html",
				context={"movie": movie})


def log_out(request):
	logout(request)
	messages.info(request, "Logged out successfully.")
	return redirect("log_in")

