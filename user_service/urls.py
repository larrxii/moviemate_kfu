from django.urls import path
import user_service.views as views

urlpatterns = [
    path('<int:user_id>/', views.user_profile, name='user_profile'),
    path('<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('<int:user_id>/reviews/', views.user_reviews, name='user_reviews'),
    path('<int:user_id>/watchlist/', views.user_watchlist, name='user_watchlist'),
    path('<int:user_id>/favorites/', views.user_favorites, name='user_favorites')
]

