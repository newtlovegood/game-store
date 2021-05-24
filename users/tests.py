from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Profile


class ProfileTests(TestCase):


    def test_create_profile_no_image(self):
        User = get_user_model()
        test_user = User.objects.cr

        profile = Profile.objects.create(user=User)
        self.assertEqual(profile.user.username)



    def test_create_profile(self):
        User = get_user_model()

        profile = Profile.objects.create(user=User,
                                         )