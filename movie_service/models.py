from django.db import models
from user_service.models import User

class Movie(models.Model):
    title = models.CharField(max_length=255)
    year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    poster = models.CharField(max_length=255, blank=True)
    is_film = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Actor(models.Model):
    full_name = models.CharField(max_length=255)
    photo = models.CharField(max_length=255, blank=True)
    year_of_birth = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.full_name

class Director(models.Model):
    full_name = models.CharField(max_length=255)
    year_of_birth = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.full_name

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Award(models.Model):
    name = models.CharField(max_length=255)
    nomination = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.year})"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user} for {self.movie}"

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gt=0, rating__lte=10), name='rating_range')
        ]

# Связующие таблицы

class MovieActor(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'actor')

class MovieAward(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    award = models.ForeignKey(Award, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'award')

class MovieDirector(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    director = models.ForeignKey(Director, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'director')

class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'genre')

class MovieCountry(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('movie', 'country')

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'movie')
