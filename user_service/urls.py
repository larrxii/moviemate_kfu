from django.urls import path
from . import views

urlpatterns = [
    path('<int:user_id>/', views.user_profile, name='user_profile'),
    path('<int:user_id>/edit/', views.edit_user, name='edit_user'),
]
