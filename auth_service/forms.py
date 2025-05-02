from django import forms
from user_service.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        error_messages={'required': 'Обязательное поле для ввода.'}
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Подтвердите пароль",
        error_messages={'required': 'Обязательное поле для ввода.'}
    )
    username = forms.CharField(
        error_messages={'required': 'Обязательное поле для ввода.'}
    )
    email = forms.EmailField(
        error_messages={'required': 'Обязательное поле для ввода.'}
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Пользователь с таким именем пользователя уже существует.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким e-mail уже существует.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Пароли не совпадают.")
        return cleaned_data

class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="E-mail",
        error_messages={
            'required': 'Обязательное поле для ввода.',
            'invalid': 'Введите корректный e-mail.'
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Пароль",
        error_messages={'required': 'Обязательное поле для ввода.'}
    )
