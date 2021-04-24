from django.db import models
from django.urls import reverse


class Game(models.Model):
    name = models.CharField(max_length=300)
    price = models.FloatField()
    genre = models.CharField(max_length=100)
    description = models.TextField(default='')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('games:detail', kwargs={'pk': self.pk})


