from django.db.models import Avg, Count, Q
from movie_service.models import Movie, Review, MovieGenre
from user_service.models import User
from .models import Recommendation
from collections import Counter


class RecommendationEngine:
    def __init__(self, user_id):
        self.user_id = user_id
        self.user = User.objects.get(id=user_id)

    def generate_recommendations(self, is_film=True, limit=10):

        user_reviews = Review.objects.filter(user=self.user)

        if user_reviews.count() < 3:
            return self._get_popular_recommendations(is_film, limit)

        rated_movie_ids = user_reviews.values_list('movie_id', flat=True)
        content_based_recs = self._get_content_based_recommendations(rated_movie_ids, is_film, limit)

        # Коллаборативная фильтрация
        collab_recs = self._get_collaborative_recommendations(rated_movie_ids, is_film, limit)

        # Объединяем рекомендации с весами
        final_recommendations = self._combine_recommendations(content_based_recs, collab_recs, limit)

        # Сохраняем рекомендации в базу данных
        self._save_recommendations(final_recommendations)

        return final_recommendations

    def _get_content_based_recommendations(self, rated_movie_ids, is_film, limit):

        user_reviews = Review.objects.filter(user=self.user, rating__gte=7)
        high_rated_movie_ids = user_reviews.values_list('movie_id', flat=True)

        if not high_rated_movie_ids:
            return []

        genre_counts = MovieGenre.objects.filter(
            movie_id__in=high_rated_movie_ids
        ).values_list('genre_id', flat=True)

        genre_counter = Counter(genre_counts)
        favorite_genres = [genre_id for genre_id, count in genre_counter.most_common(3)]

        if not favorite_genres:
            return []

        recommended_movies = Movie.objects.filter(
            is_film=is_film,
            genres__id__in=favorite_genres
        ).exclude(
            id__in=rated_movie_ids
        ).annotate(
            genre_match_count=Count('genres', filter=Q(genres__id__in=favorite_genres))
        ).order_by('-genre_match_count')[:limit]

        return [(movie, movie.genre_match_count / len(favorite_genres)) for movie in recommended_movies]

    def _get_collaborative_recommendations(self, rated_movie_ids, is_film, limit):

        user_reviews = Review.objects.filter(user=self.user)

        if not user_reviews:
            return []

        similar_users = User.objects.filter(
            reviews__movie_id__in=rated_movie_ids
        ).exclude(
            id=self.user_id
        ).annotate(
            common_reviews_count=Count('reviews', filter=Q(reviews__movie_id__in=rated_movie_ids))
        ).filter(
            common_reviews_count__gte=2  # Минимум 2 общих оценки
        )

        if not similar_users:
            return []

        # Фильмы, которые понравились таким же пользователям
        recommended_movies = Movie.objects.filter(
            is_film=is_film,
            reviews__user__in=similar_users,
            reviews__rating__gte=7  # Высокие оценки
        ).exclude(
            id__in=rated_movie_ids
        ).annotate(
            recommendation_count=Count('reviews', filter=Q(reviews__rating__gte=7))
        ).order_by('-recommendation_count')[:limit]

        return [(movie, min(movie.recommendation_count / 5, 1.0)) for movie in recommended_movies]

    def _get_popular_recommendations(self, is_film, limit):

        rated_movie_ids = Review.objects.filter(user=self.user).values_list('movie_id', flat=True)

        popular_movies = Movie.objects.filter(
            is_film=is_film
        ).exclude(
            id__in=rated_movie_ids
        ).annotate(
            avg_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews')
        ).filter(
            reviews_count__gte=5  # Минимум 5 оценок
        ).order_by('-avg_rating', '-reviews_count')[:limit]

        return [(movie, 0.5) for movie in popular_movies]  # Вес 0.5 для популярных рекомендаций

    def _combine_recommendations(self, content_based_recs, collab_recs, limit):

        # Веса для разных типов рекомендаций
        content_weight = 0.7
        collab_weight = 0.3

        # Для объединения рекомендаций
        all_recs = {}

        for movie, score in content_based_recs:
            all_recs[movie.id] = {'movie': movie, 'score': score * content_weight}

        for movie, score in collab_recs:
            if movie.id in all_recs:
                all_recs[movie.id]['score'] += score * collab_weight
            else:
                all_recs[movie.id] = {'movie': movie, 'score': score * collab_weight}

        # Сортируем по оценке
        sorted_recs = sorted(all_recs.values(), key=lambda x: x['score'], reverse=True)

        return [(rec['movie'], rec['score']) for rec in sorted_recs[:limit]]

    def _save_recommendations(self, recommendations):

        # Удаляем старые рекомендации
        Recommendation.objects.filter(user=self.user).delete()

        # Сохраняем новые рекомендации
        for movie, score in recommendations:
            Recommendation.objects.create(
                user=self.user,
                movie=movie,
                score=score
            )
