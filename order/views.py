from django.http import JsonResponse
from django.views.generic import ListView, DetailView, FormView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.contrib import messages

from order.models import Order, OrderItem
from order.forms import OrderCheckoutForm
from games.models import Game
from .cart import Cart


class UserOrderView(ListView):
    model = Order
    template_name_suffix = '_user'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        orders_qs = Order.objects.filter(customer_id=self.kwargs.get('id'))
        context['user_filtered'] = orders_qs
        if not orders_qs:
            context['no_orders'] = True
        return context


class UserCurrentOrderView(ListView):
    model = Order
    template_name_suffix = '_current'
    template_name = 'order/order_current.html'

    def get(self, request, *args, **kwargs):
        context = {}
        try:
            context['cur_order'] = Order.objects.get(ordered=False)
            return render(request, self.template_name, context)
        except Order.DoesNotExist:
            messages.info(request, 'No items in Cart')
            return redirect('/')


class AllOrdersView(UserPassesTestMixin, ListView):
    model = Order

    def test_func(self):
        return self.request.user.groups.filter(name='managers').exists()


class OrderDetailView(UserPassesTestMixin, DetailView):
    model = Order

    def test_func(self):
        return self.request.user.groups.filter(name='managers').exists()


class OrderCheckoutView(FormView):
    template_name = 'order/order_checkout.html'
    form_class = OrderCheckoutForm
    success_url = '/thanks/'

    def get_initial(self):
        initial = super(OrderCheckoutView, self).get_initial()
        if self.request.user.is_anonymous:
            return initial
        initial.update({'first_name': self.request.user.first_name,
                        'last_name': self.request.user.last_name,
                        'email': self.request.user.email})
        return initial

    def form_valid(self, form):
        order = Order.objects.filter(ordered=False)[0]
        if self.request.user.is_authenticated:
            order.customer = self.request.user
            order.save()
        order.ordered = True
        order.save()

        # set ordered for all items in order
        for item in order.items.all():
            item.ordered = True
            item.save()
        # clear basket
        cart = Cart(self.request)
        cart.clear()
        return super().form_valid(form)


def add_to_basket(request):
    cart = Cart(request)

    if request.POST.get('action') == 'post':
        # GETS game DATA FROM AJAX REQUEST
        game_id = request.POST.get('gameId')
        game_qty = int(request.POST.get('gameQty'))
        # check if game exists
        try:
            game = Game.objects.get(pk=game_id)
        except Game.DoesNotExist:
            return JsonResponse({'message': 'Game not found'})
        # CHECKS IF ANY OPEN ORDER
        order_qs = Order.objects.filter(ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            add_new_item_to_order(request,
                                  game_qty,
                                  game,
                                  order)

        else:
            # create new order
            order = Order.objects.create()

            add_new_item_to_order(request,
                                  game_qty,
                                  game,
                                  order)
        # ADDS GAME TO SESSION DICT
        actual_qty = order.items.get(item_id=game_id).quantity
        cart.add(game, actual_qty)
        # get total QTY of basket
        cart_length = cart.__len__()
        # message
        if game_qty != actual_qty:
            return JsonResponse({'message': 'Item quantity was adjusted!', 'total': order.total, 'qty': cart_length, 'instock': False})
        elif game.quantity_available == 0:
            return JsonResponse({'message': 'Item was added', 'total': order.total, 'qty': cart_length, 'instock': False})
        return JsonResponse({'message': 'Item was added', 'total': order.total, 'qty': cart_length})


def remove_from_basket(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        game_id = request.POST.get('gameId')
        game = get_object_or_404(Game, id=game_id)
        order_qs = Order.objects.filter(ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # CHECK IF THE SAME GAME IS ALREADY THERE
            if order.items.filter(item__pk=game.pk).exists():
                try:
                    order_item = order.items.get(item__pk=game.pk)
                except OrderItem.MultipleObjectsReturned:
                    order.delete()
                    cart.delete(game)
                    cart.clear()
                    return JsonResponse({'message': 'Something went wrong'})
                # delete from order
                order.items.get(item__pk=game.pk).delete()
                # update total price
                order.calculate_total()
                # update qty_available for game
                order_item.remove_game_from_cart()
                # delete order_item
                order_item.delete()
                # delete from session
                cart.delete(game)
                cart_qty = cart.__len__()
                response = {'total': order.total, 'qty': cart_qty}
                if not order.items.exists():
                    order.delete()
                    del cart
                    response = {'deleted': 0}
                return JsonResponse(response)
            else:
                return JsonResponse({'message': 'Item not in cart'})
        else:
            return JsonResponse({'message': 'Order does not exist'})

    return redirect('order:order-current')


def increment_to_basket(request):
    cart = Cart(request)
    game_id = str(request.POST.get('gameId'))
    # check if ajax called right
    if request.POST.get('action') == 'post':
        # check if game exists
        try:
            game = Game.objects.get(pk=game_id)
        except Game.DoesNotExist:
            return JsonResponse({'message': 'Game not found'})
        # check if item in basket and in order
        try:
            order = Order.objects.get(ordered=False)
            order_item = order.items.get(item_id=game_id)
        except (Order.DoesNotExist, OrderItem.DoesNotExist):
            return JsonResponse({'message': 'Order/Item not found'})

        # check if QTY-AVAILABLE enough
        if not game.is_qty_enough(1):
            return JsonResponse({'message': 'We can\'t get you more than this ! :('})


        order_item.adding_game_to_cart()
        order.calculate_total()
        # add to cart
        cart.add(game, 1)
        # cart total QTY
        cart_qty = cart.__len__()
        # response
        return JsonResponse({'qty': cart_qty, 'total': order.total})
    else:
        return redirect('order:order-current')


def reduce_from_basket(request):
    cart = Cart(request)
    game_id = str(request.POST.get('gameId'))
    # check if ajax called right
    if request.POST.get('action') == 'post':
        # check if game exists
        try:
            game = Game.objects.get(pk=game_id)
        except Game.DoesNotExist:
            return JsonResponse({'message': 'Game not found'})
        # check if item in basket and in order
        try:
            order = Order.objects.get(ordered=False)
            order_item = order.items.get(item_id=game_id)
        except (Order.DoesNotExist, OrderItem.DoesNotExist):
            return JsonResponse({'message': 'Order/Item not found'})

        if order_item.quantity == 1:
            # prevention from JS/HTML hackers
            return JsonResponse({'refresh': True})
        # game.available +1
        game.quantity_available += 1
        game.save()
        # reduce from order/item
        order_item.quantity -= 1
        order_item.save()
        # calc total in order
        order.calculate_total()
        # reduce from cart
        cart.remove(game)
        # cart total qty
        cart_qty = cart.__len__()
        # response json
        return JsonResponse({'qty': cart_qty, 'total': order.total})
    # message - something is wrong
    else:
        return redirect('order:order-current')


######## helper functions ######


def add_new_item_to_order(request, requested_qty, game, order):
    if not game.is_qty_enough(requested_qty):
        if requested_qty > game.quantity_available:
            requested_qty = game.quantity_available
    order_item = create_order_item(request, game, requested_qty)
    order.items.add(order_item)
    order_item.adding_game_to_cart(requested_qty)
    order.calculate_total()


def create_order_item(request, game, requested_qty):
    if request.user.is_authenticated:
        return OrderItem.objects.create(
            item=game,
            user=request.user,
            quantity=requested_qty,
            ordered=False
        )
    else:
        return OrderItem.objects.create(
            item=game,
            quantity=requested_qty,
            ordered=False
        )

