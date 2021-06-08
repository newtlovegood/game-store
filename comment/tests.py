from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.shortcuts import reverse

from games.models import Game
from order.models import Order, OrderItem
from .models import MPTTComment
from .forms import MPTTCommentForm


class TestMPTTCommentModel(TestCase):

    def setUp(self) -> None:
        # get Group created
        Group.objects.create(name='managers')
        # get user created
        User = get_user_model()
        self.test_user = User.objects.create_user(username='testuser1', email='test@email.com', password='password')
        # add user to managers
        managers_grp = Group.objects.get(name='managers')
        managers_grp.user_set.add(self.test_user)
        managers_grp.save()
        # login
        self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'password'}, follow=False)
        # create some additional games
        self.g1 = Game.objects.create(name='test1', description='test1', quantity_available=11, price=20.99)
        # create ORDER
        self.order = Order.objects.create(customer=self.test_user, total=20.99, ordered=False)
        # create order item
        self.order_item = OrderItem.objects.create(user=self.test_user,
                                                   item=self.g1,
                                                   quantity=1)
        # add item to order
        self.order.items.add(self.order_item)

        # create comment
        self.comment = MPTTComment.objects.create(username=self.test_user,
                                                  game=self.g1,
                                                  content='TestComment')

    def test_comment_listing(self):
        self.assertEqual(self.comment.username.username, 'testuser1')
        self.assertEqual(self.comment.game.name, 'test1')

    def test_str_comment(self):
        self.assertEqual(str(self.comment), 'TestComment')

    def test_form(self):
        form = MPTTCommentForm()
        self.assertFalse(form.fields['parent'].required)

    #### test views


class TestCommentView(TestCase):

    def setUp(self) -> None:
        # get Group created
        Group.objects.create(name='managers')
        # get user created
        User = get_user_model()
        self.test_user = User.objects.create_user(username='testuser1', email='test@email.com', password='password')
        # add user to managers
        managers_grp = Group.objects.get(name='managers')
        managers_grp.user_set.add(self.test_user)
        managers_grp.save()
        # create some additional games
        self.g1 = Game.objects.create(name='test1', description='test1', quantity_available=11, price=20.99)
        # create ORDER
        self.order = Order.objects.create(customer=self.test_user, total=20.99, ordered=False)
        # create order item
        self.order_item = OrderItem.objects.create(user=self.test_user,
                                                   item=self.g1,
                                                   quantity=1)
        # add item to order
        self.order.items.add(self.order_item)

        # create comment
        self.comment = MPTTComment.objects.create(username=self.test_user,
                                                  game=self.g1,
                                                  content='TestComment')



    def test_comment_post_view_no_parent_logged_in(self):

        # login
        self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'password'}, follow=False)

        data = {'game': self.g1.id, 'content': 'NewTestComment', 'action': 'post'}
        response = self.client.post(reverse('comments:comment-post'), data=data)


        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MPTTComment.objects.count(), 2)
        self.assertTrue(MPTTComment.objects.get(content='NewTestComment'))
        self.assertEqual(MPTTComment.objects.filter(parent=self.comment.id).count(), 0)
        self.assertEqual(MPTTComment.objects.filter(username=self.test_user).count(), 2)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'content': 'NewTestComment'})


    def test_comment_post_view_with_parent_logged_out(self):

        data = {'game': self.g1.id, 'content': 'NewTestComment', 'parent': self.comment.id, 'action': 'post'}
        response = self.client.post(reverse('comments:comment-post'), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(MPTTComment.objects.count(), 2)
        self.assertTrue(MPTTComment.objects.get(content='NewTestComment'))
        self.assertEqual(MPTTComment.objects.filter(parent=self.comment.id).count(), 1)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'content': 'NewTestComment'})


    def test_delete_comment(self):

        response = self.client.post(reverse('comments:comment-delete'), data={'id': self.comment.id,
                                                                              'action': 'post'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MPTTComment.objects.count(), 0)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'COMMENT DELETED!'})

    def test_delete_comment_404(self):

        response = self.client.post(reverse('comments:comment-delete'), data={'id': -100,
                                                                              'action': 'post'})
        self.assertEqual(response.status_code, 404)