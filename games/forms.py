from django import forms
from games.models import Game, Genre


class GameCreateForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = '__all__'
        widgets = {
            'genre': forms.CheckboxSelectMultiple(),
        }


class GameSearchForm(forms.Form):

    q = forms.CharField(max_length=100, label='', widget=forms.TextInput(attrs={'id': 'user-input', 'class': 'search-box',
                                                                                'placeholder': 'Search'}))


class GameFilterForm(forms.Form):
    genres = [
        'Strategy',
        'RPG',
        'Sports',
        'Races-Rally',
        'Races-Arcade',
        'Races-Formula',
        'Races-Off-Road',
        'Action-FPS',
        'Action-TPS',
        'Action-Misc',
        'Adventure',
        'Puzzle & Skills',
        'Other',
    ]

    prefix = 'filter'

    f = forms.ModelMultipleChoiceField(queryset=Genre.objects, label='', widget=forms.CheckboxSelectMultiple())
