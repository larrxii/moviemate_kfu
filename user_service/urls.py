from django.urls import path
from . import views

urlpatterns = [
    path('<int:user_id>/edit/', views.edit_user, name='edit_user'),
]
