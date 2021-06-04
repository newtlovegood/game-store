import uuid

from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.shortcuts import reverse

from django.contrib.auth.models import Group, AnonymousUser
from django.contrib.auth import get_user_model

from order.models import Order, OrderItem
from games.models import Game

from order.views import OrderCheckoutView, add_to_basket, remove_from_basket, increment_to_basket, reduce_from_basket
from order.forms import OrderCheckoutForm


class TestOrderViews(TestCase):

    def setUp(self) -> None:
        # request factory
        self.factory = RequestFactory()
        self.middleware = SessionMiddleware()
        # get Group created
        Group.objects.create(name='managers')
        # get user created
        User = get_user_model()
        self.test_user = User.objects.create_user(username='testuser1', email='test@email.com', password='password')
        self.test_user.first_name = 'testfirstname'
        self.test_user.last_name = 'testlastname'
        self.test_user.save()
        # add user to managers
        self.managers_grp = Group.objects.get(name='managers')
        self.managers_grp.user_set.add(self.test_user)
        self.managers_grp.save()
        # login
        self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'password'}, follow=False)
        # create game object
        self.game = Game.objects.create(
            name='TestGame',
            price=10.99,
            description='Test Game description',
            quantity_available=100
        )
        # create some additional games
        g1 = Game.objects.create(name='test1', description='test1', quantity_available=11, price=20.99)
        g2 = Game.objects.create(name='test2', description='test2', quantity_available=10, price=10)
        # create ORDER
        self.order = Order.objects.create(customer=self.test_user, total=20.99, ordered=False)
        # create order item
        self.order_item = OrderItem.objects.create(user=self.test_user,
                                                   item=g1,
                                                   quantity=1)
        self.order_item_extra = OrderItem.objects.create(user=self.test_user,
                                                         item=g2,
                                                         quantity=5)
        # add item to order
        self.order.items.add(self.order_item)
        self.order.items.add(self.order_item_extra)

    def test_user_order_view_with_orders(self):
        response = self.client.get(reverse('order:order-user', kwargs={'id': self.test_user.pk}))
        self.assertTemplateUsed(response, 'order/order_user.html')
        self.assertEqual(response.status_code, 200)
        # found filtered
        self.assertTrue(response.context['user_filtered'])

    def test_user_order_view_without_orders(self):
        # remove order
        self.order.customer = None
        self.order.save()
        response = self.client.get(reverse('order:order-user', kwargs={'id': self.test_user.pk}))
        self.assertTemplateUsed(response, 'order/order_user.html')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['no_orders'])

    def test_user_current_order(self):

        response = self.client.get(reverse('order:order-current'))
        self.assertTemplateUsed(response, 'order/order_current.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cart')
        # check context
        self.assertTrue(response.context['cur_order'])
        # remove cur_order
        self.order.ordered = True
        self.order.save()
        response_no_order = self.client.get(reverse('order:order-current'))
        self.assertEqual(response_no_order.status_code, 302)

    def test_all_orders(self):
        response = self.client.get(reverse('order:order-all'))
        self.assertEqual(response.status_code, 200)

        # remove user from group
        self.managers_grp.user_set.remove(self.test_user)
        response_no_group = self.client.get(reverse('order:order-all'))
        self.assertEqual(response_no_group.status_code, 403)

    def test_order_detail(self):
        # set order to ORDERED
        self.order.ordered = True
        self.order.save()
        response = self.client.get(reverse('order:order-detail', kwargs={'pk': self.order.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '20.99')
        # remove user from group
        self.managers_grp.user_set.remove(self.test_user)
        response_no_group = self.client.get(reverse('order:order-detail', kwargs={'pk': self.test_user.pk}))
        self.assertEqual(response_no_group.status_code, 403)

    def test_order_checkout(self):
        response = self.client.get(reverse('order:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order/order_checkout.html')
        self.assertContains(response, 'Proceed')
        self.assertTrue(response.context['form'])

    def test_checkout_form_valid(self):
        # set customer
        self.order.customer = None
        self.order.save()
        # set sessions middleware
        request = self.factory.post(reverse('order:checkout'), data={'phone': '123123123'})
        self.middleware.process_request(request)
        request.session.save()
        request.user = self.test_user
        # init request factory view
        view = OrderCheckoutView()
        view.setup(request)
        # init form for request factory
        form = OrderCheckoutForm()
        view.form_valid(form)
        self.order.refresh_from_db()
        self.order_item.refresh_from_db()
        self.order_item_extra.refresh_from_db()
        # self.assertEqual(request.status_code, 200)
        self.assertEqual(self.order.customer, self.test_user)
        self.assertTrue(self.order.ordered)
        self.assertTrue(self.order_item.ordered)
        self.assertTrue(self.order_item_extra.ordered)

    def test_order_checkout_initial_form(self):
        response = self.client.get(reverse('order:checkout'))
        # logged in
        self.assertContains(response, 'testfirstname')
        self.assertContains(response, 'testlastname')
        self.assertContains(response, 'email.com')
        # anon
        self.client.post(reverse('account_logout'))
        response_anon = self.client.get(reverse('order:checkout'))
        self.assertNotContains(response_anon, 'email.com')


class TestAddView(TestCase):

    def setUp(self) -> None:
        # request factory
        self.factory = RequestFactory()
        self.middleware = SessionMiddleware()
        # get Group created
        Group.objects.create(name='managers')
        # get user created
        User = get_user_model()
        self.test_user = User.objects.create_user(username='testuser1', email='test@email.com', password='password')
        self.test_user.first_name = 'testfirstname'
        self.test_user.last_name = 'testlastname'
        self.test_user.save()
        # add user to managers
        self.managers_grp = Group.objects.get(name='managers')
        self.managers_grp.user_set.add(self.test_user)
        self.managers_grp.save()
        # login
        self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'password'}, follow=False)
        # create game object
        self.game = Game.objects.create(
            name='TestGame',
            price=10.99,
            description='Test Game description',
            quantity_available=100)
        self.game_for_cart = Game.objects.create(
            name='TestGameExtra',
            price=10,
            description='Test Game description',
            quantity_available=1)
        # create some additional games
        g1 = Game.objects.create(name='test1', description='test1', quantity_available=11, price=20.99)
        g2 = Game.objects.create(name='test2', description='test2', quantity_available=10, price=10)
        # create ORDER
        self.order = Order.objects.create(customer=self.test_user, total=20.99, ordered=False)
        # create order item
        self.order_item = OrderItem.objects.create(user=self.test_user,
                                                   item=g1,
                                                   quantity=1)
        self.order_item_extra = OrderItem.objects.create(user=self.test_user,
                                                         item=g2,
                                                         quantity=5)
        self.order_item_for_cart = OrderItem.objects.create(user=self.test_user,
                                                            item=self.game_for_cart,
                                                            quantity=1)
        # add item to order
        self.order.items.add(self.order_item)
        self.order.items.add(self.order_item_extra)
        self.order.items.add(self.order_item_for_cart)

    def test_add_to_basket_game_exists_new_order(self):
        request = self.factory.post(reverse('order:add-to-cart'), data={'action': 'post',
                                                                        'gameId': self.game.id,
                                                                        'gameQty': 1})
        # set sessions middleware
        self.middleware.process_request(request)
        request.session.save()
        request.user = self.test_user
        # get response from VIEW
        response = add_to_basket(request)

        # game exists
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {"message": "Item was added", "total": 10.99, "qty": 1})
        # Create New order
        self.assertEqual(Order.objects.all().count(), 1)
        self.assertEqual(Order.objects.all()[0].total, 10.99)
        self.assertEqual(Order.objects.all()[0].items.all()[0],
                         OrderItem.objects.get(item=self.game))
        # CART CHECK
        self.assertTrue(request.session['cart'][str(self.game.id)])
        self.assertEqual(len(request.session['cart']), 1)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'Item was added', 'total': 10.99, 'qty': 1})

    def test_add_to_basket_game_exists_existing_order(self):
        request = self.factory.post(reverse('order:add-to-cart'), data={'action': 'post',
                                                                        'gameId': self.game.id,
                                                                        'gameQty': 1})
        # set sessions middleware
        self.middleware.process_request(request)
        request.session.save()
        # init cart with any game INITIALY
        request.session.update(
            {'cart': {str(self.game_for_cart.id): {'item_price': self.game_for_cart.price, 'qty': 1}}})
        request.session.save()
        request.user = self.test_user
        # get response from VIEW
        response = add_to_basket(request)
        # check add_new_item_to_order
        self.assertEqual(response.status_code, 200)
        self.assertTrue(OrderItem.objects.all().count(), 4)
        self.assertTrue(self.order.items.get(item=self.game))
        self.assertTrue(self.game.quantity_available, 99)
        self.assertTrue(self.order.total, 91.98)

    def test_add_to_basket_game_exists_existing_order_anon(self):
        request = self.factory.post(reverse('order:add-to-cart'), data={'action': 'post',
                                                                        'gameId': self.game.id,
                                                                        'gameQty': 1})
        # set sessions middleware
        self.middleware.process_request(request)
        request.session.save()
        # init cart with any game INITIALY
        request.session.update(
            {'cart': {str(self.game_for_cart.id): {'item_price': self.game_for_cart.price, 'qty': 1}}})
        request.session.save()
        request.user = AnonymousUser()
        # get response from VIEW
        response = add_to_basket(request)
        # check add_new_item_to_order
        self.assertEqual(response.status_code, 200)
        self.assertTrue(OrderItem.objects.all().count(), 4)
        self.assertTrue(self.order.items.get(item=self.game))
        self.assertTrue(self.game.quantity_available, 99)
        self.assertTrue(self.order.total, 91.98)

    def test_add_to_basket_game_not_found(self):
        # create uuid
        game_id_not_exists = uuid.uuid4()
        # game not found
        request = self.factory.post(reverse('order:add-to-cart'), data={'action': 'post',
                                                                        'gameId': game_id_not_exists,
                                                                        'gameQty': 1})
        # set sessions middleware
        self.middleware.process_request(request)
        request.session.save()
        request.user = self.test_user
        response = add_to_basket(request)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'Game not found'})

    def test_add_to_basket_responses(self):
        request = self.factory.post(reverse('order:add-to-cart'), data={'action': 'post',
                                                                        'gameId': self.game_for_cart.id,
                                                                        'gameQty': 1})

        # set sessions middleware
        self.middleware.process_request(request)
        request.session.save()
        request.user = self.test_user
        # get response from VIEW
        response = add_to_basket(request)
        total = Order.objects.all()[0].total
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'Item was added', 'total': total, 'qty': 1, 'instock': False})

    def test_add_to_basket_responses_1(self):
        request = self.factory.post(reverse('order:add-to-cart'), data={'action': 'post',
                                                                        'gameId': self.game_for_cart.id,
                                                                        'gameQty': 3})

        # set sessions middleware
        self.middleware.process_request(request)
        request.session.save()
        request.user = self.test_user
        # get response from VIEW
        response = add_to_basket(request)
        total = Order.objects.all()[0].total
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'Item quantity was adjusted!', 'total': total, 'qty': 1, 'instock': False})


class TestRemoveView(TestCase):

    def setUp(self) -> None:
        self.view = add_to_basket
        # request factory
        self.factory = RequestFactory()
        self.middleware = SessionMiddleware()
        # get Group created
        Group.objects.create(name='managers')
        # get user created
        User = get_user_model()
        self.test_user = User.objects.create_user(username='testuser1', email='test@email.com', password='password')
        self.test_user.first_name = 'testfirstname'
        self.test_user.last_name = 'testlastname'
        self.test_user.save()
        # add user to managers
        self.managers_grp = Group.objects.get(name='managers')
        self.managers_grp.user_set.add(self.test_user)
        self.managers_grp.save()
        # login
        self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'password'}, follow=False)
        # create game object
        self.game = Game.objects.create(
            name='TestGame',
            price=10.99,
            description='Test Game description',
            quantity_available=100)
        self.game_for_cart = Game.objects.create(
            name='TestGameExtra',
            price=10,
            description='Test Game description',
            quantity_available=1)
        # create some additional games
        g1 = Game.objects.create(name='test1', description='test1', quantity_available=11, price=20)
        g2 = Game.objects.create(name='test2', description='test2', quantity_available=10, price=10)
        # create ORDER
        self.order = Order.objects.create(customer=self.test_user, total=20.99, ordered=False)
        # create order item
        self.order_item = OrderItem.objects.create(user=self.test_user,
                                                   item=g1,
                                                   quantity=1)
        self.order_item_extra = OrderItem.objects.create(user=self.test_user,
                                                         item=g2,
                                                         quantity=5)
        self.order_item_for_cart = OrderItem.objects.create(user=self.test_user,
                                                            item=self.game_for_cart,
                                                            quantity=1)
        # add item to order
        self.order.items.add(self.order_item)
        self.order.items.add(self.order_item_extra)
        self.order.items.add(self.order_item_for_cart)

    def _setup(self, action=True, order_filler=False, game_id=None, qty=None):
        data = {'gameId': game_id if game_id else self.game.id,
                'gameQty': qty if qty else 1}
        if action:
            data.update({'action': 'post'})

        request = self.factory.post(reverse('order:remove-from-cart'), data=data)
        # set sessions middleware
        self.middleware.process_request(request)
        request.session.save()
        request.user = self.test_user

        if order_filler:
            request.session.update(
                {'cart': {str(self.game_for_cart.id): {'item_price': self.game_for_cart.price, 'qty': 1}}})

        return request

    def test_action_not_passed(self):
        response = self.client.post(reverse('order:remove-from-cart'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn((reverse('order:order-current'), 302), response.redirect_chain)

    def test_order_not_exists(self):
        response = remove_from_basket(self._setup())
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'Order does not exist'})

    def test_order_exists_game_in(self):
        request = self._setup(order_filler=True, game_id=self.game_for_cart.id)
        response = remove_from_basket(request)
        # if game is listed TWO times
        # if only one game found
        order = Order.objects.all()[0]
        self.assertFalse(OrderItem.objects.filter(item=self.game_for_cart).exists())
        self.assertEqual(order.items.all().count(), 2)
        self.assertEqual(order.total, 70)
        # check cart
        self.assertNotIn(str(self.game_for_cart.id), request.session['cart'])
        self.assertEqual(len(request.session['cart']), 0)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'total': order.total, 'qty': 0})

    def test_order_exists_game_in_try_except(self):
        # add additional SAME item to order
        order = Order.objects.all()[0]
        extra_item = OrderItem.objects.create(user=self.test_user,
                                              item=self.game_for_cart,
                                              quantity=5)
        order.items.add(extra_item)
        request = self._setup(order_filler=True, game_id=self.game_for_cart.id)
        response = remove_from_basket(request)
        # check cart
        self.assertNotIn(str(self.game_for_cart.id), request.session['cart'])
        self.assertEqual(len(request.session['cart']), 0)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'Something went wrong'})

    def test_order_exists_game_in_last_item_deleted(self):
        order = Order.objects.all()[0]
        # empty the cart
        order.items.get(item__name='test1').delete()
        order.calculate_total()
        order.items.get(item__name='test2').delete()
        order.calculate_total()
        request = self._setup(order_filler=True, game_id=self.game_for_cart.id)
        response = remove_from_basket(request)
        # if game is listed TWO times
        # if only one game found
        self.assertFalse(OrderItem.objects.filter(item=self.game_for_cart).exists())
        self.assertEqual(order.items.all().count(), 0)
        # check cart
        self.assertNotIn(str(self.game_for_cart.id), request.session['cart'])
        self.assertEqual(len(request.session['cart']), 0)

        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'deleted': 0})

    def test_order_exists_game_not_in_order(self):
        response = remove_from_basket(self._setup(order_filler=True))
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'Item not in cart'})


class TestIncrementView(TestCase):

    def setUp(self) -> None:
        self.view = add_to_basket
        # request factory
        self.factory = RequestFactory()
        self.middleware = SessionMiddleware()
        # get Group created
        Group.objects.create(name='managers')
        # get user created
        User = get_user_model()
        self.test_user = User.objects.create_user(username='testuser1', email='test@email.com', password='password')
        self.test_user.first_name = 'testfirstname'
        self.test_user.last_name = 'testlastname'
        self.test_user.save()
        # add user to managers
        self.managers_grp = Group.objects.get(name='managers')
        self.managers_grp.user_set.add(self.test_user)
        self.managers_grp.save()
        # login
        self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'password'}, follow=False)
        # create game object
        self.game = Game.objects.create(
            name='TestGame',
            price=10.99,
            description='Test Game description',
            quantity_available=100)
        self.game_for_cart = Game.objects.create(
            name='TestGameExtra',
            price=10,
            description='Test Game description',
            quantity_available=1)
        # create some additional games
        g1 = Game.objects.create(name='test1', description='test1', quantity_available=11, price=20)
        g2 = Game.objects.create(name='test2', description='test2', quantity_available=10, price=10)
        # create ORDER
        self.order = Order.objects.create(customer=self.test_user, total=20.99, ordered=False)
        # create order item
        self.order_item = OrderItem.objects.create(user=self.test_user,
                                                   item=g1,
                                                   quantity=1)
        self.order_item_extra = OrderItem.objects.create(user=self.test_user,
                                                         item=g2,
                                                         quantity=5)
        self.order_item_for_cart = OrderItem.objects.create(user=self.test_user,
                                                            item=self.game_for_cart,
                                                            quantity=1)
        # add item to order
        self.order.items.add(self.order_item)
        self.order.items.add(self.order_item_extra)
        self.order.items.add(self.order_item_for_cart)

    def _setup(self, action=True, order_filler=False, game_id=None):
        data = {'gameId': game_id if game_id else self.game.id}
        if action:
            data.update({'action': 'post'})

        request = self.factory.post(reverse('order:remove-from-cart'), data=data)
        # set sessions middleware
        self.middleware.process_request(request)
        request.session.save()
        request.user = self.test_user

        if order_filler:
            request.session.update(
                {'cart': {str(self.game_for_cart.id): {'item_price': self.game_for_cart.price, 'qty': 1}}})

        return request

    def test_action_not_passed(self):
        response = self.client.post(reverse('order:increment-to-cart'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn((reverse('order:order-current'), 302), response.redirect_chain)

    def test_no_game_exists(self):
        game_not_exists = uuid.uuid4()
        response = increment_to_basket(self._setup(game_id=game_not_exists))
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'Game not found'})

    def test_item_not_in_order(self):
        response = increment_to_basket(self._setup())
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'Order/Item not found'})

    def test_game_exists_not_enough_qty(self):
        self.game_for_cart.quantity_available = 0
        self.game_for_cart.save()
        response = increment_to_basket(self._setup(order_filler=True, game_id=self.game_for_cart.id))
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'We can\'t get you more than this ! :('})

    def test_game_exists_qty_available(self):
        request = self._setup(order_filler=True, game_id=self.game_for_cart.id)
        response = increment_to_basket(request)

        self.order_item_for_cart.refresh_from_db()
        self.game_for_cart.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(self.order_item_for_cart.quantity, 2)
        self.assertEqual(self.game_for_cart.quantity_available, 0)
        self.assertEqual(self.order.total, 90)
        # check cart
        self.assertIn(str(self.game_for_cart.id), request.session['cart'])
        self.assertEqual(len(request.session['cart']), 1)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'qty': 2, 'total': 90})


class TestReduceView(TestCase):

    def setUp(self) -> None:
        self.view = add_to_basket
        # request factory
        self.factory = RequestFactory()
        self.middleware = SessionMiddleware()
        # get Group created
        Group.objects.create(name='managers')
        # get user created
        User = get_user_model()
        self.test_user = User.objects.create_user(username='testuser1', email='test@email.com', password='password')
        self.test_user.first_name = 'testfirstname'
        self.test_user.last_name = 'testlastname'
        self.test_user.save()
        # add user to managers
        self.managers_grp = Group.objects.get(name='managers')
        self.managers_grp.user_set.add(self.test_user)
        self.managers_grp.save()
        # login
        self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'password'}, follow=False)
        # create game object
        self.game = Game.objects.create(
            name='TestGame',
            price=10.99,
            description='Test Game description',
            quantity_available=100)
        self.game_for_cart = Game.objects.create(
            name='TestGameExtra',
            price=10,
            description='Test Game description',
            quantity_available=1)
        # create some additional games
        g1 = Game.objects.create(name='test1', description='test1', quantity_available=11, price=20)
        g2 = Game.objects.create(name='test2', description='test2', quantity_available=10, price=10)
        # create ORDER
        self.order = Order.objects.create(customer=self.test_user, total=20.99, ordered=False)
        # create order item
        self.order_item = OrderItem.objects.create(user=self.test_user,
                                                   item=g1,
                                                   quantity=1)
        self.order_item_extra = OrderItem.objects.create(user=self.test_user,
                                                         item=g2,
                                                         quantity=5)
        self.order_item_for_cart = OrderItem.objects.create(user=self.test_user,
                                                            item=self.game_for_cart,
                                                            quantity=1)
        # add item to order
        self.order.items.add(self.order_item)
        self.order.items.add(self.order_item_extra)
        self.order.items.add(self.order_item_for_cart)

    def _setup(self, action=True, order_filler=False, game_id=None):
        data = {'gameId': game_id if game_id else self.game.id}
        if action:
            data.update({'action': 'post'})

        request = self.factory.post(reverse('order:remove-from-cart'), data=data)
        # set sessions middleware
        self.middleware.process_request(request)
        request.session.save()
        request.user = self.test_user

        if order_filler:
            request.session.update(
                {'cart': {str(self.game_for_cart.id): {'item_price': self.game_for_cart.price, 'qty': 1}}})

        return request

    def test_action_not_passed(self):
        response = self.client.post(reverse('order:reduce-in-cart'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn((reverse('order:order-current'), 302), response.redirect_chain)

    def test_no_game_exists(self):
        game_not_exists = uuid.uuid4()
        response = reduce_from_basket(self._setup(game_id=game_not_exists))
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'Game not found'})

    def test_item_not_in_order(self):
        response = reduce_from_basket(self._setup())
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'message': 'Order/Item not found'})

    def test_normal_reduce(self):
        self.order_item_for_cart.quantity = 2
        self.order_item_for_cart.save()

        request = self._setup(game_id=self.game_for_cart.id)
        request.session.update(
            {'cart': {str(self.game_for_cart.id): {'item_price': self.game_for_cart.price, 'qty': 2}}})
        response = reduce_from_basket(request)

        self.order_item_for_cart.refresh_from_db()
        self.game_for_cart.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(self.game_for_cart.quantity_available, 2)
        self.assertEqual(self.order_item.quantity, 1)
        self.assertEqual(self.order.total, 80)
        # check cart
        self.assertIn(str(self.game_for_cart.id), request.session['cart'])
        self.assertEqual(len(request.session['cart']), 1)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'qty': 1, 'total': 80})

    def test_reduce_if_one_item_remained(self):
        request = self._setup(order_filler=True, game_id=self.game_for_cart.id)
        response = reduce_from_basket(request)

        self.order_item_for_cart.refresh_from_db()
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             {'refresh': True})
