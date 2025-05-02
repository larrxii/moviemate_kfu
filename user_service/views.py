from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.db.models import Avg, Count
from .models import User
from .forms import UserEditForm, UserPasswordChangeForm
from movie_service.models import Review, MovieGenre

def profile_view(request):
    return render(request, 'user_service/profile.html')