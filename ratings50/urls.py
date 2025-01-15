from django.contrib import admin
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path("register", views.register, name="register"),
    path('', views.index, name='index'),
    path('new', views.new_movie, name='new'),
    path('movie/<int:movie_id>', views.movie, name="movie"),
    path('edit/<int:movie_id>', views.edit, name="edit"),
    path('editlog/<int:movie_id>', views.editlog, name="editlog"),
    path('search', views.search, name="search"),
    #APIs
    path('movie/rate', views.rate, name="rate"),
    path('movie/reviews/<int:movie_id>', views.reviews, name="reviews"),
    path('movie/vote_review', views.vote_review, name="vote_review"),
    path('tmdb_search', views.tmdb_search, name="tmdb_search"),
    path('tmdb_data', views.tmdb_data, name="tmdb_data")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)