from django.test import TestCase
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from unittest import mock

from .models import Profile
from order.models import Order, OrderItem
from games.models import Game


class ProfileTests(TestCase):

    def test_profile_creation_with_signals(self):
        User = get_user_model()
        test_user = User.objects.create_user(username='testuser1', email='test@email.com', password='password')
        # signals create profile
        profile = Profile.objects.get(user=test_user.id)
        self.assertEqual(profile.user.username, 'testuser1')
        self.assertEqual(profile.user.email, 'test@email.com')
        self.assertEqual(profile.user.profile, profile)

    def test_profile_update_status_code(self):
        self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'secret'}, follow=False)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)



