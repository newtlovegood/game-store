from django.db import models


class Game(models.Model):
    name = models.CharField(max_length=300)
    price = models.FloatField()
    genre = models.CharField(max_length=100)



