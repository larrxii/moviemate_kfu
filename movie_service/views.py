from django.shortcuts import render
from movie_service.models import Movie, Genre
from movie_service.forms import MovieFilterForm


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