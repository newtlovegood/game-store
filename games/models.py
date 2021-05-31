import uuid
from django.db import models
from django.urls import reverse
from django.core.validators import MaxValueValidator


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

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    name = models.CharField(max_length=300)
    price = models.FloatField(default=0, blank=True)
    description = models.TextField(default='')
    genre = models.ManyToManyField(Genre, blank=True)
    image = models.ImageField(upload_to='images/games', default='images/games/default.jpg', null=True, blank=True)
    quantity_available = models.IntegerField(validators=[MaxValueValidator(7858772994)], default=0, blank=True)

    class Meta:
        ordering = ['-quantity_available']

    def get_absolute_url(self):
        # using this mostly for redirects in CBVs
        return reverse('games:detail', kwargs={'pk': self.pk})

    def is_qty_enough(self, requested_qty):
        if self.quantity_available < requested_qty:
            return False
        return True

    def __str__(self):
        return self.name


