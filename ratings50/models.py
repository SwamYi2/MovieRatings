from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.db.models import Avg

# Create your models here.
class User(AbstractUser):
    pass

class Genre(models.Model):
    name = models.CharField(max_length=64)
    def __str__(self):
        return f"{self.name}"

class Certification(models.Model):
    name = models.CharField(max_length=10)
    def __str__(self):
        return f"{self.name}"

class Movie(models.Model):
    title = models.CharField(max_length=64)
    overview = models.CharField(max_length=512)
    genre = models.ManyToManyField(Genre, related_name='movie', blank=True)
    release_date = models.DateField(blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    poster = models.ImageField(upload_to="posters", blank=True, default=None)
    trailer_url = models.URLField(blank=True, null=True)
    director = models.CharField(max_length=32, blank=True, default=None)
    tmdb_id = models.IntegerField(blank=True, null=True)
    certification = models.ForeignKey(Certification, default=None, on_delete=models.PROTECT)
    def __str__(self):
        return f"{self.title} {self.upload_date}"

    def avg_rating(self):
        avg = self.ratings.aggregate(Avg('score'))['score__avg']
        if avg:
            avg = round(avg, 1)
        return avg

    # Crop the poster to 3:2 on save
    def save(self, *args, **kwargs):
        if self.poster != None and self.poster != False:

            try:
                pil_image_obj = Image.open(self.poster)
            except ValueError:
                super(Movie, self).save(*args, **kwargs)
                return

            org_width, org_height = pil_image_obj.size
            if org_width > (2 * org_height) / 3:
                width = (2 * org_height) / 3
                left = (org_width / 2) - (width / 2)

                new_image = pil_image_obj.crop((left, 0, left + width, org_height))

                new_image_io = BytesIO()
                new_image.save(new_image_io, format='JPEG')

                temp_name = self.poster.name
                self.poster.delete(save=False)  

                self.poster.save(
                    temp_name,
                    content=ContentFile(new_image_io.getvalue()),
                    save=False
                )

        super(Movie, self).save(*args, **kwargs)

    # delete poster when Movie object is deleted
    def delete(self, using=None, keep_parents=False):
        if self.poster.name != "posters/poster_not_available.jpg":
            self.poster.storage.delete(self.poster.name)
        super().delete()

class EditLog(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    changes = models.CharField(max_length=700)
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.movie.title}, {self.user.username}"

class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    score = models.IntegerField()

    class Meta:
        unique_together = ('movie', 'user')

    def __str__(self):
        return f"{self.movie.title}, {self.user.username}, {self.score}"

class Review(models.Model):
    rating = models.ForeignKey(Rating, on_delete=models.PROTECT)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    headline = models.CharField(max_length=64)
    text = models.CharField(max_length=500)
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('movie', 'user')
    def serialize(self, user):

        # check if the user has voted this review
        if not user.is_anonymous:
            try:
                vote = self.votes.get(user=user)
                up_voted = vote.up
                down_voted = not vote.up
            except Vote.DoesNotExist:
                up_voted, down_voted = False, False

            deleteable = self.user == user
        else:
            up_voted, down_voted = False, False
            deleteable = False

        return {
            "id": self.id,
            "rating_score": self.rating.score,
            "username": self.user.username,
            "headline": self.headline,
            "text": self.text,
            "date": self.date.strftime("%b %d %Y, %I:%M %p"),
            "up_voted": up_voted,
            "down_voted": down_voted,
            "votes": self.votes.filter(up=True).count() - self.votes.filter(up=False).count(),
            "deleteable": deleteable
        }
    def __str__(self):
        return f"{self.movie.title}, {self.user.username}"

class Vote(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    up = models.BooleanField()
    class Meta:
        unique_together = ('review', 'user')
