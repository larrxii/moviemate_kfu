from django import forms
from .models import Genre

class MovieFilterForm(forms.Form):
    search_text = forms.CharField(
        required=False,
        label="Поиск по названию",
        widget=forms.TextInput(attrs={'placeholder': 'Введите название'})
    )
    
    genres = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Genre.objects.all(),
        label="Жанры",
        widget=forms.CheckboxSelectMultiple
    )
    
    year_from = forms.IntegerField(
        required=False,
        label="Год от",
        widget=forms.NumberInput(attrs={'placeholder': 'От'})
    )
    
    year_to = forms.IntegerField(
        required=False,
        label="Год до",
        widget=forms.NumberInput(attrs={'placeholder': 'До'})
    )