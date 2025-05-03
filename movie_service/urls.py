from django.urls import path, include
import movie_service.views as views

urlpatterns = [
    path('catalog/', views.catalog_view, name="film_catalog"),
    path('<int:movie_id>/', views.movie_view, name="movie_page"),
    path('<int:movie_id>/review/', views.add_review, name='add_review'),
    path('top/', views.top_content_view, name='top_content'),
]