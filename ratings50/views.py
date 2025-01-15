from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.shortcuts import render
from django.core import serializers
from .models import Movie, Genre, Certification, User, EditLog, Rating, Review, Vote
from django.db import IntegrityError
from django import forms
from django.core.paginator import Paginator
import json
import requests

# Insert your own TMDB Api key here
API_KEY = ''

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'overview', 'release_date', 'poster', 'trailer_url', 'director', 'certification', 'genre', 'tmdb_id']
        widgets = {
            'release_date': forms.DateInput(attrs={'type': 'date'}),
            'genre' : forms.CheckboxSelectMultiple(),
            'overview': forms.Textarea(),
        }

class SearchForm(forms.Form):
    title = forms.CharField(label="Find a movie", required=False)
    genre = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    

# Create your views here.
def index(request):
    movies = Movie.objects.all().order_by('-upload_date')
    p = Paginator(movies, 10)
    page_id = request.GET.get('page')
    if page_id == None:
        page_id = 1
    page = p.page(page_id)
    return render(request, "ratings50/index.html", {"page": page, "pagination": True})

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "ratings50/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "ratings50/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "ratings50/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "ratings50/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "ratings50/register.html")

@login_required(login_url='login')
def new_movie(request):
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            movie = form.save(commit=False)

            # If there's no poster, add a defult one
            if movie.poster != None:
                print("poster found")
                movie.poster.name = f"{movie.title} poster.jpg"
            else:
                movie.poster = "posters/poster_not_available.jpg"

            # Edit the Youtube URL to embed
            if movie.trailer_url != None:
                url_tuple = movie.trailer_url.split("/")
                youtube_key = url_tuple[-1].replace("watch?v=", "")
                movie.trailer_url = "https://www.youtube.com/embed/" + youtube_key
            movie.save()
            
            # Add many2many field after saving
            form.save_m2m()

            edit = EditLog(
                movie = movie,
                user = request.user,
                changes = "item created"
            )
            edit.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            print(form.errors.as_data())
            return render(request, "ratings50/movie_form.html", {'form': form, 'new': True})

    return render(request, "ratings50/movie_form.html", {'form': MovieForm(), 'new': True})

def movie(request, movie_id):
    try:
        movie = Movie.objects.get(id=movie_id)
    except Movie.DoesNotExist:
        return render(request, "ratings50/index.html", {"page": None,
         "heading": "The movie you're trying to visit does not exist", 
         "pagination": False})


    # Add user's rating info to the movie
    if request.user.is_authenticated:
        movie.user_rating = Rating.objects.filter(movie=movie, user=request.user).first()
    
    return render(request, "ratings50/movie.html", {'movie': movie})

def search(request):
    if request.method == "GET":
        form = SearchForm()

        return render(request, "ratings50/search.html", {'form': form})

    form = SearchForm(request.POST)

    if form.is_valid():
        # use title if the user specified it
        if form.cleaned_data['title'] != "":
            results = Movie.objects.filter(title__icontains=form.cleaned_data['title'])
        else:
            results = Movie.objects.all()
        
        # save genre name strings to use it in the heading
        genre_names = []
        for genre in form.cleaned_data['genre']:
            results = results.filter(genre__id=genre.id)
            genre_names.append(genre.name)
        
        heading = ""
        if form.cleaned_data['title'] != "":
            heading += "Title: " +'"'+ form.cleaned_data['title'] + '" '
        if genre_names != []:
            heading += "Genre: " + ', '.join(genre_names)
        return render(request, "ratings50/index.html", {"page": results, "heading": heading, "pagination": False})

@login_required(login_url='login')
def edit(request, movie_id):

    if request.method == 'GET':
        movie = Movie.objects.get(id=movie_id)
        
        form = MovieForm(instance=movie)
        return render(request, "ratings50/movie_form.html", {
            'form': form,
            'new': False,
            'movie_id': movie.id
            })

    new_data = MovieForm(request.POST, request.FILES)
    if new_data.is_valid():
        # get the old movie to compare with the new one
        old = serializers.serialize('python', Movie.objects.filter(id=movie_id))
        old = old[0]

        changes = []
        for new_field in new_data.cleaned_data.items():
            key = new_field[0]
            value = new_field[1]

            # skip poster, certification and genre because they're not simple fields
            if key == 'poster' or key == 'certification' or key == 'genre':
                continue

            # compare the remaining fields
            if old['fields'][key] != value:
                changes.append(f"{key}: {value}")

        # create tuples of ids and names to compare
        list_of_genre_ids = []
        list_of_genre_names = []
        for genre in new_data.cleaned_data['genre']:
            list_of_genre_ids.append(Genre.objects.get(name=genre).id)
            list_of_genre_names.append(genre)
        if old['fields']['genre'] != list_of_genre_ids:
            changes.append(f"Genre: {list_of_genre_names}")

        # Compare certification
        if old['fields']['certification'] != Certification.objects.get(name=new_data.cleaned_data['certification']).id:
            changes.append(f"Certification: {new_data.cleaned_data['certification']}")

        # check if there's a new poster
        poster_changed = False
        if new_data.cleaned_data['poster'] != None:
            changes.append(f"Poster is updated")
            poster_changed = True

    movie = Movie.objects.get(id=movie_id)

    # If the user uploaded a new poster, delete the old one
    if poster_changed and movie.poster.name != "posters/poster_not_available.jpg":
        movie.poster.delete()

    edited_form = MovieForm(request.POST, request.FILES, instance=movie)
    if edited_form.is_valid():
        edited_movie = edited_form.save(commit=False)
        # Change the poster file name
        if poster_changed:
            edited_movie.poster.name = f"{edited_movie.title} poster.jpg"

        # Edit the Youtube URL to embed
        if movie.trailer_url != None:
            url_tuple = movie.trailer_url.split("/")
            youtube_key = url_tuple[-1].replace("watch?v=", "")
            movie.trailer_url = "https://www.youtube.com/embed/" + youtube_key

        edited_movie.save()
        edited_form.save_m2m()
    
    # Save the Edit History
    if changes:
        edit = EditLog(
                movie = movie,
                user = request.user,
                changes = "\n".join(changes)
            )
        edit.save()

    return HttpResponseRedirect(reverse('movie', kwargs={
    'movie_id': movie_id
    }))

def editlog(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    editlog = EditLog.objects.filter(movie=movie).order_by('-date')
    
    return render(request, "ratings50/editlog.html", {"editlog": editlog, "title": movie.title})

# API
@csrf_exempt
def rate(request):

    if request.user.is_anonymous:
        return JsonResponse({"Error": "You need to log in"}, status=400)

    data = json.loads(request.body)
    movie_id = data.get("movie_id")
    score = data.get("score")
    movie = Movie.objects.get(id=movie_id)

    if int(score) > 10 or int(score) < 0 :
        return JsonResponse({"Error": "Invalid rating score"}, status=400)

    # update or create the rating
    obj, created = Rating.objects.update_or_create(
    movie=movie, user=request.user,
    defaults={'score': score},
    )

    movie = Movie.objects.get(id=movie_id)
    user_rating = score

    return JsonResponse({
        "avg_rating": movie.avg_rating(),
         "user_rating": user_rating}, 
         status=201)

@csrf_exempt
def reviews(request, movie_id):
    # Return all reviews of a movie
    if request.method == "GET":
        movie = Movie.objects.get(id=movie_id)
        reviews = Review.objects.filter(movie=movie).order_by('-date')
        reviews = [review.serialize(request.user) for review in reviews]

        return JsonResponse({'reviews': reviews}, safe=False)
    # post a review
    elif request.method == "POST":
        data = json.loads(request.body)
        headline = data.get("headline")
        text = data.get("review")
        movie = Movie.objects.get(id=movie_id)

        if request.user.is_anonymous:
            return JsonResponse({"Error": "You need to Log in to post a review"}, status=400)

        # Check if the user has rated the movie first
        try:
            rating = Rating.objects.get(user=request.user, movie=movie)
        except Rating.DoesNotExist:
            return JsonResponse({"Error": "You need to rate the movie first"}, status=400)

        review = Review(
            movie = movie,
            rating = rating,
            headline = headline,
            text = text,
            user = request.user
        )
        try:
            review.save()
        except IntegrityError:
            return JsonResponse({"Error": "Duplicate reviews are not allowed"}, status=400)

        return JsonResponse({"message": "Success"}, status=201)

    # Delete a review
    elif request.method == "PUT":
        data = json.loads(request.body)
        review_id = data.get("review_id")
        action = data.get("action")
        review = Review.objects.get(id=review_id)

        # don't delete if the user is not the owner
        if review.user != request.user or request.user.is_anonymous:
            return JsonResponse({"Error": "Only the owner can delete the review"}, status=400)

        if review.user == request.user and action == 'delete':
            review.delete()
            return JsonResponse({"message": "Successfully deleted"}, status=201)
        

@csrf_exempt
def vote_review(request):
    data = json.loads(request.body)
    review_id = data.get("review_id")
    up = data.get("up")

    if request.user.is_anonymous:
        return JsonResponse({"Error": "You need to Log in to vote the review"}, status=400)

    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return JsonResponse({"Error": "The review you're trying to vote has been deleted"}, status=400)

    # Check if the user already has a vote
    try:
        vote = Vote.objects.get(review=review, user=request.user)

        # if the user is voting the same, they're trying to cancel the vote
        if vote.up == up:
            vote.delete()
            up_voted, down_voted = False, False
        else:
            vote.up = up
            vote.save()
            up_voted, down_voted = vote.up, not vote.up
    # If this is a new vote, create one
    except Vote.DoesNotExist:
        vote = Vote(
            review = review,
            user = request.user,
            up = up
        )
        vote.save()
        up_voted, down_voted = vote.up, not vote.up

    votes = review.votes.filter(up=True).count() - review.votes.filter(up=False).count()
    return JsonResponse({"up_voted": up_voted, "down_voted": down_voted, "vote_count": votes}, status=201)
        
@csrf_exempt
def tmdb_search(request):
    data = json.loads(request.body)
    query = data.get("query")
    year = data.get("year")

    movies = requests.get("https://api.themoviedb.org/3/search/movie?api_key="+ API_KEY +"&page=1&query="+ query +"&year="+ year).json()
    return JsonResponse({"results": movies}, status=201)

@csrf_exempt
def tmdb_data(request):
    data = json.loads(request.body)
    id = data.get("id")

    movie = requests.get("https://api.themoviedb.org/3/movie/"+ id +"?api_key="+ API_KEY +"&append_to_response=release_dates,credits,videos&language=en-US").json()
    return JsonResponse({"data": movie}, status=201)