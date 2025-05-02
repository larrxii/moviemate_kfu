from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import User

class UserEditForm(forms.ModelForm):
    username = forms.CharField(
        label="Имя пользователя",
        error_messages={'required': 'Обязательное поле для ввода.'}
    )
    email = forms.EmailField(
        label="E-mail",
        error_messages={
            'required': 'Обязательное поле для ввода.',
            'invalid': 'Введите корректный e-mail.'
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"E-mail '{email}' уже используется.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        qs = User.objects.filter(username=username).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(f"Имя пользователя '{username}' уже занято.")
        return username


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Старый пароль",
        widget=forms.PasswordInput,
        error_messages={'required': 'Обязательное поле для ввода.'}
    )
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput,
        error_messages={'required': 'Обязательное поле для ввода.'}
    )
    new_password2 = forms.CharField(
        label="Подтвердите новый пароль",
        widget=forms.PasswordInput,
        error_messages={'required': 'Обязательное поле для ввода.'}
    )

    def clean_new_password2(self):
        new1 = self.cleaned_data.get('new_password1')
        new2 = self.cleaned_data.get('new_password2')
        if not new1 or not new2:
            raise forms.ValidationError('Обязательное поле для ввода.')
        if new1 != new2:
            raise forms.ValidationError('Пароли не совпадают.')
        return new2

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not old_password:
            raise forms.ValidationError('Обязательное поле для ввода.')
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                'Старый пароль введён неверно. Пожалуйста, попробуйте ещё раз.',
                code='invalid'
            )
        return old_password


