from django import forms
from games.models import Game


class GameCreateForm(forms.ModelForm):

    class Meta:
        model = Game
        fields = '__all__'
        widgets = {
            'genre': forms.CheckboxSelectMultiple(),
        }


class GameSearchForm(forms.Form):

    q = forms.CharField(max_length=100, label='Search')

