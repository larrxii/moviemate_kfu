from django.urls import path, include
import movie_service.views as views

urlpatterns = [
    path('catalog/', views.catalog_view, name="film_catalog")
]