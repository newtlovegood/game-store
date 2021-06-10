import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group


class Command(BaseCommand):
    help = 'creates superuser'

    def handle(self, *args, **options):
        # DJANGO_SU_NAME = 'admin'
        # DJANGO_SU_EMAIL = 'admin@email.com'
        # DJANGO_SU_PASSWORD = 'password'

        DJANGO_SU_NAME = os.environ['SUPERUSER_NAME']
        DJANGO_SU_EMAIL = os.environ['SUPERUSER_EMAIL']
        DJANGO_SU_PASSWORD = os.environ['SUPERUSER_PASS']

        # create group
        if not Group.objects.filter(name='managers').exists():
            grp_managers = Group.objects.create(name='managers')
        else:
            grp_managers = Group.objects.get(name='managers')

        if not User.objects.filter(username=DJANGO_SU_NAME).exists():

            superuser = User.objects.create_superuser(
                username=DJANGO_SU_NAME,
                email=DJANGO_SU_EMAIL,
                password=DJANGO_SU_PASSWORD)

            grp_managers.user_set.add(superuser)

        grp_managers.user_set.add(User.objects.get(username=DJANGO_SU_NAME))



