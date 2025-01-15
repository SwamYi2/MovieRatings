from django.contrib import admin
from .models import Movie, Rating, Review, EditLog, Genre

# Register your models here.
admin.site.register(Movie)
admin.site.register(Rating)
admin.site.register(Review)
admin.site.register(EditLog)
admin.site.register(Genre)