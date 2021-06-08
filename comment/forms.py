from django import forms
from mptt.forms import TreeNodeChoiceField

from .models import MPTTComment


class MPTTCommentForm(forms.ModelForm):

    parent = TreeNodeChoiceField(queryset=MPTTComment.objects.all())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['parent'].required = False

    class Meta:
        model = MPTTComment
        fields = ('content', 'game', 'parent')

