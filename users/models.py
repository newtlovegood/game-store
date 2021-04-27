from django.db import models
from django.contrib.auth import models


class User(models.User, models.PermissionsMixin):

    def __str__(self):
        return f"{self.username}"


class Group(models.Group):


    def __str__(self):
        return self.name
