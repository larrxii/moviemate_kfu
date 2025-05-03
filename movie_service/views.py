from django.shortcuts import get_object_or_404, redirect
from movie_service.models import Favorites, Movie, Genre, Review, Watchlist
from movie_service.forms import MovieFilterForm
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


def catalog_view(request):
    queryset = Movie.objects.all()
    
    filter_form = MovieFilterForm(request.GET or None)
    if filter_form.is_valid():
        if filter_form.cleaned_data.get('genres'):
            selected_genres = filter_form.cleaned_data['genres']
            
            for genre in selected_genres:
                queryset = queryset.filter(genres=genre)
    
        if filter_form.cleaned_data.get('year_from'):
            queryset = queryset.filter(year__gte=filter_form.cleaned_data['year_from'])
        
        if filter_form.cleaned_data.get('year_to'):
            queryset = queryset.filter(year__lte=filter_form.cleaned_data['year_to'])
        
        if filter_form.cleaned_data.get('search_text'):
            queryset = queryset.filter(title__icontains=filter_form.cleaned_data['search_text'])
    
    all_genres = Genre.objects.all()
    
    context = {
        'movies': queryset,
        'filter_form': filter_form,
        'genres': all_genres,
    }
    
    return render(request, 'movie_service/catalog.html', context)


def movie_view(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    in_watchlist = False
    if request.user.is_authenticated:
        in_watchlist = Watchlist.objects.filter(user=request.user, movie=movie).exists()

    in_favorites = False
    if request.user.is_authenticated:
        in_favorites = Favorites.objects.filter(user=request.user, movie=movie).exists()

    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(user=request.user, movie=movie).first()

    context = {
        'movie': movie,
        'user_review': user_review,
        'in_watchlist': in_watchlist,
        'in_favorites': in_favorites,
    }
    
    return render(request, 'movie_service/movie_page.html', context)


def top_content_view(request):
    
    is_film = request.GET.get('type', 'film') == 'film'
    per_page = int(request.GET.get('per_page', 10))
    page_number = request.GET.get('page', 1)

    queryset = Movie.objects.filter(is_film=is_film).annotate(
        avg_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews')
    ).filter(reviews_count__gt=0).order_by('-avg_rating', '-reviews_count')
    
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'is_film': is_film,
        'per_page': per_page,
        'content_type': 'film' if is_film else 'series'
    }
    
    return render(request, 'movie_service/top_content.html', context)

@login_required(login_url='/auth/login')
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    # Check if user already left review to film
    existing_review = Review.objects.filter(user=request.user, movie=movie).first()

    if existing_review:
        messages.error(request, 'Вы уже оставили отзыв на этот фильм.')
        return redirect('movie_page', movie_id=movie_id)

    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        text = request.POST.get('text', '')

        if not 1 <= rating <= 10:
            messages.error(request, 'Оценка должна быть от 1 до 10.')
            return redirect('movie_page', movie_id=movie_id)

        Review.objects.create(
            user=request.user,
            movie=movie,
            rating=rating,
            text=text
        )
        messages.success(request, 'Ваш отзыв добавлен.')

        return redirect('movie_page', movie_id=movie_id)


    return redirect('movie_page', movie_id=movie_id)


@login_required(login_url='/auth/login')
def add_to_watchlist(request, movie_id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, pk=movie_id)

        watchlist_item, created = Watchlist.objects.get_or_create(
            user=request.user,
            movie=movie
        )

        if created:
            messages.success(request, 'Фильм добавлен в список "Буду смотреть."')
        else:
            messages.info(request, 'Этот фильм уже в вашем списке.')

    return redirect('movie_page', movie_id=movie_id)


@login_required(login_url='/auth/login')
def remove_from_watchlist(request, movie_id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, pk=movie_id)

        deleted, _ = Watchlist.objects.filter(
            user=request.user,
            movie=movie
        ).delete()

        if deleted:
            messages.success(request, 'Фильм удален из списка "Буду смотреть".')
        else:
            messages.info(request, 'Этого фильма нет в вашем списке.')

    return redirect('movie_page', movie_id=movie_id)

@login_required(login_url='/auth/login')
def add_to_favorites(request, movie_id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, pk=movie_id)

        favorites_item, created = Favorites.objects.get_or_create(
            user = request.user,
            movie=movie
        )

        if created:
            messages.success(request, 'Фильм добавлен в список "Любимое"')
        else:
            messages.info(request, 'Этот фильм уже в вашем списке "Любимое"')
    
    return redirect('movie_page', movie_id=movie_id)



@login_required(login_url='/auth/login')
def remove_from_favorites(request, movie_id):
    if request.method == 'POST':
        movie = get_object_or_404(Movie, pk=movie_id)

        deleted, _ = Favorites.objects.filter(
            user=request.user,
            movie=movie
        ).delete()

        if deleted:
            messages.success(request, 'Фильм удален из списка "Любимое".')
        else:
            messages.info(request, 'Этого фильма нет в вашем списке.')

    return redirect('movie_page', movie_id=movie_id)