from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth import get_user_model
from django.shortcuts import reverse

from unittest import mock

from .models import Profile
from order.models import Order, OrderItem
from games.models import Game
from .views import ProfileUpdate


class ProfileTests(TestCase):

    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.middleware = SessionMiddleware()

        User = get_user_model()
        self.test_user = User.objects.create_user(username='testuser1', email='test@email.com', password='password')
        # signals create profile
        self.profile = Profile.objects.get(user=self.test_user.id)

    def test_profile_creation_with_signals(self):
        self.assertEqual(self.profile.user.username, 'testuser1')
        self.assertEqual(self.profile.user.email, 'test@email.com')
        self.assertEqual(self.profile.user.profile, self.profile)

    def test_profile_str(self):
        self.assertEqual(str(self.profile), 'testuser1 Profile')

    def test_profile_image(self):
        profile_image = SimpleUploadedFile(name='test_image.jpg',
                                           content=open('media/images/profiles/test.jpg', 'rb').read(),
                                           content_type='image/jpeg')
        profile_image.height = 1000
        profile_image.width = 100

        self.profile.image = profile_image
        self.profile.save()

        self.assertTrue(self.profile.image.height <= 500)
        self.assertTrue(self.profile.image.width <= 500)

    def test_profile_update_view(self):
        # login
        self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'password'}, follow=False)

        response = self.client.get(reverse('profile'))
        self.assertTrue(response.context['form_user'])
        self.assertTrue(response.context['form_profile'])

        # post
        with open('media/images/profiles/test.jpg', 'rb') as img:
            request = self.factory.post(reverse('profile'), data={'email': 'new@email.com',
                                                                  'username': 'newUsername',
                                                                  'image': img})
            request.user = self.test_user
            response = ProfileUpdate.as_view()(request)
            self.test_user.refresh_from_db()

            self.assertEqual(response.status_code, 302)
            self.assertEqual(self.test_user.email, 'new@email.com')
            self.assertEqual(self.test_user.username, 'newUsername')

    def test_profile_update_view_failed_form(self):
        # login
        self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'password'}, follow=False)

        request = self.factory.post(reverse('profile'), data={'email': 1111})
        request.user = self.test_user
        self.middleware.process_request(request)
        request.session.save()
        response = ProfileUpdate.as_view()(request)
        self.test_user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.test_user.email, 'test@email.com')
