from django.urls import path
import user_service.views as views

urlpatterns = [
    path('{user_id:int}/', views.profile_view, name="profile")
]