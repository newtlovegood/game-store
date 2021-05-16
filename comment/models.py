from django.db import models
from django.conf import settings
from django.urls import reverse

from games.models import Game


class Comment(models.Model):

    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=600)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children', blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.username}'s comment"

    def get_absolute_url(self):
        return reverse('games:detail', kwargs={'pk': self.game_id})

