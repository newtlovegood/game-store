from django.test import TestCase
from django.shortcuts import reverse

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from order.models import Order, OrderItem
from games.models import Game


class TestOrder(TestCase):

    def setUp(self) -> None:
        # get Group created
        Group.objects.create(name='managers')
        # get user created
        User = get_user_model()
        test_user = User.objects.create_user(username='testuser1', email='test@email.com', password='password')
        # add user to managers
        managers_grp = Group.objects.get(name='managers')
        managers_grp.user_set.add(test_user)
        managers_grp.save()
        # login
        self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'password'}, follow=False)
        # create some additional games
        g1 = Game.objects.create(name='test1', description='test1', quantity_available=11, price=20.99)
        g2 = Game.objects.create(name='test2', description='test2', quantity_available=10, price=10)
        # create ORDER
        self.order = Order.objects.create(customer=test_user, total=20.99, ordered=False)
        # create order item
        self.order_item = OrderItem.objects.create(user=test_user,
                                                   item=g1,
                                                   quantity=1)
        self.order_item_extra = OrderItem.objects.create(user=test_user,
                                                   item=g2,
                                                   quantity=5)
        # add item to order
        self.order.items.add(self.order_item)
        self.order.items.add(self.order_item_extra)

    def test_order_item_listing(self):
        self.assertEqual(self.order_item.user.username, 'testuser1')
        self.assertEqual(self.order_item.item.name, 'test1')

    def test_order_listing(self):
        self.assertEqual(self.order.customer.username, 'testuser1')
        self.assertEqual(self.order.total, 20.99)
        self.assertEqual(self.order.ordered, False)

    def test_order_has_order_item(self):
        self.assertEqual(self.order.items.count(), 2)

    # test ORDER_ITEM methods
    def test_adding_game_to_cart_with_args(self):
        self.order_item.adding_game_to_cart(10)
        self.assertEqual(self.order_item.quantity, 10)
        self.assertEqual(self.order_item.item.quantity_available, 1)

    def test_adding_game_to_cart_without_args(self):
        self.order_item.adding_game_to_cart()
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.item.quantity_available, 10)

    def test_remove_game_from_cart_with_args(self):
        self.order_item.remove_game_from_cart(10)
        self.assertEqual(self.order_item.item.quantity_available, 21)

    def test_remove_game_from_cart_without_args(self):
        self.order_item.remove_game_from_cart()
        self.assertEqual(self.order_item.item.quantity_available, 12)

    def test_calculate_sub_total(self):
        self.assertEqual(self.order_item.calculate_sub_total(), 20.99)
        self.order_item.quantity = 5
        self.order_item.save()
        self.assertEqual(self.order_item.calculate_sub_total(), 20.99*5)

    def test_str_order_item(self):
        self.assertEqual(str(self.order_item), "1 piece(s) of test1 - NOT ordered")

    # test ORDER methods

    def test_order_calculate_total(self):
        self.order.calculate_total()
        self.assertEqual(self.order.total, 70.99)

    def test_destroy_order(self):
        self.order.reset_items_qty_available()
        self.assertEqual(self.order.items.all()[0].item.quantity_available, 12)
        self.assertEqual(self.order.items.all()[1].item.quantity_available, 15)

    def test_str_order(self):
        self.assertEqual(str(self.order), "testuser1's order - NOT ordered")