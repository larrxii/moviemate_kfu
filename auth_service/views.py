from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from .forms import UserRegistrationForm, UserLoginForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('/auth/login')
    else:
        form = UserRegistrationForm()
    return render(request, 'auth_service/register.html', {'form': form})

def login_view(request):
    error = None
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('/') # TODO: Replace it to his profile
            else:
                error = "Неверный email или пароль."
    else:
        form = UserLoginForm()
    return render(request, 'auth_service/login.html', {'form': form, 'error': error})

@require_POST
def logout_view(request):
    logout(request)
    return redirect('login')

