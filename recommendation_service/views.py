from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from user_service.models import User
from .services import RecommendationEngine
from .models import Recommendation


@login_required(login_url='/auth/login')
def user_recommendations(request, user_id):

    if request.user.id != user_id:
        raise PermissionDenied("Вы можете видеть только свои рекомендации.")

    user = get_object_or_404(User, pk=user_id)

    content_type = request.GET.get('type', 'film')
    is_film = content_type == 'film'

    # Generating recommendations
    engine = RecommendationEngine(user_id)
    recommendations = engine.generate_recommendations(is_film=is_film)

    if not recommendations:
        recommendations = [(rec.movie, rec.score) for rec in Recommendation.objects.filter(
            user=user,
            movie__is_film=is_film
        )]

    context = {
        'recommendations': recommendations,
        'is_film': is_film,
        'content_type': 'фильмов' if is_film else 'сериалов',
        'user': user
    }

    return render(request, 'recommendation_service/user_recommendations.html', context)
