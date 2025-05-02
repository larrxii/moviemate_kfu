from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import User
from .forms import UserEditForm, UserPasswordChangeForm

@login_required(login_url='/auth/login')
def edit_user(request, user_id):
    user_to_edit = get_object_or_404(User, pk=user_id)

    if request.user != user_to_edit:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user_to_edit)
        pwd_form = UserPasswordChangeForm(request.user, request.POST)
        if 'save_profile' in request.POST and form.is_valid():
            form.save()
            return redirect('profile', user_id=user_to_edit.id)
        elif 'change_password' in request.POST and pwd_form.is_valid():
            user = pwd_form.save()
            update_session_auth_hash(request, user)  # Чтобы не разлогинило
            return redirect('profile', user_id=user_to_edit.id)
    else:
        form = UserEditForm(instance=user_to_edit)
        pwd_form = UserPasswordChangeForm(request.user)

    return render(request, 'user_service/edit_user.html', {
        'form': form,
        'pwd_form': pwd_form,
    })
