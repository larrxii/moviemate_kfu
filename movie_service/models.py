from django.db import models
from user_service.models import User

class Movie(models.Model):
    title = models.CharField(max_length=255)
    year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    poster = models.CharField(max_length=255, blank=True)
    is_film = models.BooleanField(default=True)

    actors = models.ManyToManyField('Actor', through='MovieActor', related_name='movies')
    directors = models.ManyToManyField('Director', through='MovieDirector', related_name='movies')
    genres = models.ManyToManyField('Genre', through='MovieGenre', related_name='movies')
    countries = models.ManyToManyField('Country', through='MovieCountry', related_name='movies')
    awards = models.ManyToManyField('Award', through='MovieAward', related_name='movies')

    class Meta:
        db_table = 'movies'

    def __str__(self):
        return self.title

class Actor(models.Model):
    full_name = models.CharField(max_length=255)
    photo = models.CharField(max_length=255, blank=True)
    year_of_birth = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'actors'

    def __str__(self):
        return self.full_name

class Director(models.Model):
    full_name = models.CharField(max_length=255)
    year_of_birth = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'directors'

    def __str__(self):
        return self.full_name

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'genres'

    def __str__(self):
        return self.name

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'countries'

    def __str__(self):
        return self.name

class Award(models.Model):
    name = models.CharField(max_length=255)
    nomination = models.CharField(max_length=255, blank=True)
    year = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'awards'

    def __str__(self):
        return f"{self.name} ({self.year})"

class ReviewManager(models.Manager):
    def create_review(self, user, movie, rating, text=''):
        if rating < 1 or rating > 10:
            raise ValueError('Rating must be between 1 and 10')
        review = self.model(user=user, movie=movie, rating=rating, text=text)
        review.save(using=self._db)
        return review

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ReviewManager()
    def __str__(self):
        return f"Review by {self.user} for {self.movie}"

    class Meta:
        db_table = 'reviews'
        constraints = [
            models.CheckConstraint(check=models.Q(rating__gt=0, rating__lte=10), name='rating_range')
        ]
        unique_together = ('user', 'movie')

# Связующие таблицы

class MovieActor(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)

    class Meta:
        db_table = 'movie_actors'
        unique_together = ('movie', 'actor')

class MovieAward(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    award = models.ForeignKey(Award, on_delete=models.CASCADE)

    class Meta:
        db_table = 'movie_awards'
        unique_together = ('movie', 'award')

class MovieDirector(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    director = models.ForeignKey(Director, on_delete=models.CASCADE)

    class Meta:
        db_table = 'movie_directors'
        unique_together = ('movie', 'director')

class MovieGenre(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        db_table = 'movie_genres'
        unique_together = ('movie', 'genre')

class MovieCountry(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        db_table = 'movie_countries'
        unique_together = ('movie', 'country')


class WatchlistManager(models.Manager):
    def add_to_watchlist(self, user, movie):
        watchlist_item, created = self.get_or_create(user=user, movie=movie)
        return watchlist_item

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    objects = WatchlistManager()

    class Meta:
        db_table = 'watchlists'
        unique_together = ('user', 'movie')
        
    def __str__(self):
        return f"{self.user} added {self.movie} to watchlist"
