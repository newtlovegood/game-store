from django.db import models
from django.conf import settings
from django.urls import reverse

from mptt.models import MPTTModel, TreeForeignKey

from games.models import Game


class MPTTComment(MPTTModel):
    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=600)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['-timestamp']

    def __str__(self):
        return f"{self.content}"


class Comment(models.Model):

    username = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=600)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, related_name='children', blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.content}"

