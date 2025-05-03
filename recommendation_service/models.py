from django.db import models
from user_service.models import User
from movie_service.models import Movie


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    score = models.FloatField()  # Оценка релевантности рекомендации
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendations'
        unique_together = ('user', 'movie')
        ordering = ['-score']

    def __str__(self):
        return f"Recommendation of {self.movie.title} for {self.user.username}"
