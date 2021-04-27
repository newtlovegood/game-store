from django.forms import ModelForm, CheckboxSelectMultiple
from games.models import Game


class GameCreateForm(ModelForm):

    class Meta:
        model = Game
        fields = '__all__'
        widgets = {
            'genre': CheckboxSelectMultiple(),
        }
