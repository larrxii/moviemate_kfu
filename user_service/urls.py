from django.urls import path
from . import views

urlpatterns = [
    path('<int:user_id>/', views.user_profile, name='user_profile'),
    path('<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('<int:user_id>/reviews/', views.user_reviews, name='user_reviews'),
    path('<int:user_id>/watchlist/', views.user_watchlist, name='user_watchlist'),
    path('<int:user_id>/watchlist/remove/<int:movie_id>/', views.remove_from_watchlist, name='remove_from_watchlist'),
]
