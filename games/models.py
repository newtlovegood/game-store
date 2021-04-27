from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField


class Genre(models.Model):
    genres = [

        ('Strategy', 'Strategy'),
        ('RPG', 'RPG'),
        ('Sports', 'Sports'),
        ('Races/Rally', 'Races/Rally'),
        ('Races/Arcade', 'Races/Arcade'),
        ('Races/Formula', 'Races/Formula'),
        ('Races/Off-Road', 'Races/Off-Road'),
        ('Action/FPS', 'Action/FPS'),
        ('Action/TPS', 'Action/TPS'),
        ('Action/Misc', 'Action/Misc'),
        ('Adventure', 'Adventure'),
        ('Puzzle/Skills', 'Puzzle/Skills'),
        ('Other', 'Other'),
    ]

    name = models.CharField(unique=True, max_length=100, choices=genres)

    def __str__(self):
        return self.name


class Game(models.Model):

    name = models.CharField(max_length=300)
    price = models.FloatField()
    description = models.TextField(default='')
    genre = models.ManyToManyField(Genre, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # using this mostly for redirects in CBVs
        return reverse('games:detail', kwargs={'pk': self.pk})





