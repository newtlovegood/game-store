from django.views.generic import ListView, DetailView, FormView
from django.shortcuts import get_list_or_404, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages

from order.models import Order, OrderItem
from order.forms import OrderCheckoutForm
from games.models import Game


class UserOrderView(ListView):

    model = Order
    template_name_suffix = '_user'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_filtered'] = get_list_or_404(Order.objects.filter(customer_id=self.kwargs.get('id')))
        return context


class UserCurrentOrderView(ListView):

    model = Order
    template_name_suffix = '_current'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cur_order'] = get_object_or_404(Order.objects.filter(ordered=False))
        return context


class AllOrdersView(ListView):

    model = Order


class OrderDetailView(DetailView):

    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders_filtered'] = OrderItem.objects.all()
        return context


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

    def get_confirm_message(self, **kwargs):
        context = super(OrderCheckoutView, self).get_context_data()
        context['messages'] = messages.info(self.request, 'Order is confirmed by GameStore')
        return context

    def form_valid(self, form):
        if self.request.user.is_anonymous:
            order = Order.objects.filter(ordered=False)[0]
        else:
            order = Order.objects.filter(customer=self.request.user, ordered=False)[0]
        order.ordered = True
        order.save()
        # set ordered for all items in order
        for item in order.items.all():
            item.ordered = True
            item.save()
        self.get_confirm_message()
        return super().form_valid(form)


def add_to_cart(request, pk):
    item = get_object_or_404(Game, pk=pk)
    if request.user.is_anonymous:
        order_item = OrderItem.objects.create(
            item=item,
            ordered=False
        )
        order_qs = Order.objects.filter(ordered=False)

    else:
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(customer=request.user, ordered=False)

    # checks if Unordered order exists
    if order_qs.exists():
        # takes the first of unordered
        order = order_qs[0]
        # checks if THIS game already added to order
        if order.items.filter(item__pk=item.pk).exists():
            print('ok1')
            # check if item has enough qty
            if item.quantity_available > 0:
                # adds +1 to current order item
                order_item.quantity += 1
                order_item.save()
                # temp remove 1 from quantity available
                order_item.adding_game_to_cart()
                order.increase_total(item)
                messages.info(request, "Added quantity Item")
                return redirect("games:detail", pk=pk)
            else:
                messages.info(request, 'No more available!')
                return redirect('games:detail', pk=pk)

        else:
            order.items.add(order_item)
            # temp remove 1 from quantity available
            order_item.adding_game_to_cart()
            order.increase_total(item)
            messages.info(request, "Item added to your cart")
            return redirect("games:detail", pk=pk)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(customer=request.user, date=ordered_date)
        order.items.add(order_item)
        # temp remove 1 from quantity available
        order_item.adding_game_to_cart()
        order.increase_total(item)
        messages.info(request, "Item added to your cart")
        return redirect("games:detail", pk=pk)


def remove_from_cart(request, pk):
    # takes an item(game)
    item = get_object_or_404(Game, pk=pk)
    # takes all order of user which are not ordered
    order_qs = Order.objects.filter(
        customer=request.user,
        ordered=False
    )
    if order_qs.exists():
        # take only the first one
        order = order_qs[0]
        # checks if THIS game IN order
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]

            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                order_item.remove_game_from_cart()
            else:
                # deletes item
                order_item.delete()
                order_item.remove_game_from_cart()
            order.reduce_total(item)
            # in case no more items in order - it is deleted
            if not order.items.exists():
                order.delete()
                return redirect("games:detail", pk=pk)
            messages.info(request, "Item \""+order_item.item.name+"\" remove from your cart")
            return redirect("games:detail", pk=pk)
        else:
            messages.info(request, "This Item not in your cart")
            return redirect("games:detail", pk=pk)
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("games:detail", pk=pk)


#### helper functions


