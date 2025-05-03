from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import Avg, Count
from django.core.paginator import Paginator
from .models import User
from .forms import UserEditForm, UserPasswordChangeForm
from movie_service.models import Review, MovieGenre, Watchlist, Favorites

# Edit Section
@login_required(login_url='/auth/login')
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(User, pk=user_id)

    if request.user != user_to_edit:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_to_edit)
        pwd_form = UserPasswordChangeForm(request.user, request.POST)
        if 'save_profile' in request.POST and form.is_valid():
            form.save()
            return redirect('profile', user_id=user_to_edit.id)
        elif 'change_password' in request.POST and pwd_form.is_valid():
            user = pwd_form.save()
            update_session_auth_hash(request, user)  # Чтобы не разлогинило
            return redirect('profile', user_id=user_to_edit.id)
    else:
        form = UserEditForm(instance=user_to_edit)
        pwd_form = UserPasswordChangeForm(request.user)

    return render(request, 'user_service/edit_user.html', {
        'form': form,
        'pwd_form': pwd_form,
    })

# Profile Section
@login_required(login_url='/auth/login')
def user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    user_reviews = Review.objects.filter(user=user)

    reviews_count = user_reviews.count()

    avg_rating = user_reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    bad_count = 0
    good_count = 0
    excellent_count = 0
    masterpiece_count = 0

    for review in user_reviews:
        if 1 <= review.rating <= 4:
            bad_count += 1
        elif 5 <= review.rating <= 7:
            good_count += 1
        elif 8 <= review.rating <= 9:
            excellent_count += 1
        elif review.rating == 10:
            masterpiece_count += 1

    rating_distribution = {
        'Плохо': bad_count,
        'Хорошо': good_count,
        'Отлично': excellent_count,
        'Шедевр': masterpiece_count,
    }

    high_rated_movies = user_reviews.filter(rating__gte=8).values_list('movie_id', flat=True)

    genre_counts = MovieGenre.objects.filter(
        movie_id__in=high_rated_movies
    ).values(
        'genre__name'
    ).annotate(
        count=Count('genre')
    ).order_by('-count')

    favorite_genre = genre_counts.first() if genre_counts.exists() else None

    top_movies = user_reviews.select_related('movie').order_by('-rating', '-created_at')[:5]

    context = {
        'profile_user': user,
        'reviews_count': reviews_count,
        'avg_rating': round(avg_rating, 1),
        'rating_distribution': rating_distribution,
        'favorite_genre': favorite_genre['genre__name'] if favorite_genre else None,
        'top_movies': top_movies,
        'is_own_profile': request.user.id == user.id,
    }

    return render(request, 'user_service/profile.html', context)

@login_required(login_url='/auth/login')
def user_reviews(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    reviews = Review.objects.filter(user=user).select_related('movie').order_by('-created_at')

    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'user_service/reviews.html', {
        'profile_user': user,
        'reviews': page_obj,
        'is_own_profile': request.user.id == user.id,
    })

@login_required(login_url='/auth/login')
def user_watchlist(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    watchlist = Watchlist.objects.filter(user=user).select_related('movie').order_by('-id')

    paginator = Paginator(watchlist, 10) # 10 фильмов на одной странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'user_service/watchlist.html', {
        'profile_user': user,
        'watchlist': page_obj,
        'is_own_profile': request.user.id == user.id,
    })

@login_required(login_url='/auth/login')
def remove_from_watchlist(request, movie_id):
    if request.method == 'POST':
        Watchlist.objects.filter(user=request.user, movie_id=movie_id).delete()
    return redirect('user_watchlist', user_id=request.user.id)

@login_required(login_url='/auth/login')
def user_favorites(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    favorite_list = Favorites.objects.filter(user=user).select_related('movie').order_by('-id')

    paginator = Paginator(favorite_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'user_service/favorites.html', {
        'profile_user': user,
        'favorites': page_obj,
        'is_own_profile': request.user.id == user.id,
    })

@login_required(login_url='/auth/login')
def remove_from_favorites(request, movie_id):
    if request.method == 'POST':
        Favorites.objects.filter(user=request.user, movie_id=movie_id).delete()

    return redirect('user_favorites', user_id=request.user.id)
    