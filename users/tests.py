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


class UsersViewTests(TestCase):

    def setUp(self):
        self.game = mock.Mock(spec=Game)
        self.order = Order.objects.create()
        order_item = mock.create_autospec(OrderItem)
        self.order_item = order_item()
        # self.order_item.id = mock.Mock()
        User = get_user_model()
        self.credentials = {
            'username': 'testuser',
            'email': 'test@email.com',
            'password': 'secret'}
        self.user = User.objects.create_user(**self.credentials)

    def test_profile_update_view(self):
        pass

    def test_custom_login(self):
        # create anon order which is unordered
        self.order.ordered = False
        # login
        response = self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'secret'}, follow=False)
        # print('RESPONSE BELOW')
        # check if user is authenticated
        self.assertTrue(response.context['user'].is_authenticated)
        # print(response.context['user'])
        # check if order is assigned to user
        Order.objects.create()
        print(Order.objects.filter(ordered=False)[0].customer)
        print(response.context['user'])
        order_processed = Order.objects.filter(ordered=False)[0]
        # print(order_processed)
        self.assertEqual(order_processed.customer, self.user)

    def test_custom_logout(self):
        pass
