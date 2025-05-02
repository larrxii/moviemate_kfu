from django.shortcuts import get_object_or_404, render
from movie_service.models import Movie, Genre, Review
from movie_service.forms import MovieFilterForm
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Avg, Count


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

    context = {
        'movie': movie,
    }
    
    return render(request, 'movie_service/movie_page.html', context)


def top_content_view(request):
    
    is_film = request.GET.get('type', 'film') == 'film'
    per_page = int(request.GET.get('per_page', 10))
    page_number = request.GET.get('page', 1)
    
    queryset = Movie.objects.filter(is_film=is_film).annotate(
        avg_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews')
    ).order_by('-avg_rating', '-reviews_count')
    
    paginator = Paginator(queryset, per_page)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'is_film': is_film,
        'per_page': per_page,
        'content_type': 'film' if is_film else 'series'
    }
    
    return render(request, 'movie_service/top_content.html', context)
