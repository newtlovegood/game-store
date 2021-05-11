# from django.db import models
# from django.contrib.auth import models
#
#
# class User(models.User, models.PermissionsMixin):
#
#     def __str__(self):
#         return f"{self.username}"
#
#
# class Group(models.Group):
#
#     def __str__(self):
#         return self.name
#
#
# User._meta.get_field('email')._unique = True
# User._meta.get_field('email').blank = False
# User._meta.get_field('email').null = False
#
