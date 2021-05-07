from django.views.generic import ListView, DetailView
from django.shortcuts import get_list_or_404, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Sum
from django.db.models.signals import post_save

from order.models import Order, OrderItem
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
        context['cur_order'] = get_object_or_404(Order.objects.filter(customer_id=self.kwargs.get('id')).filter(ordered=False))
        return context


class AllOrdersView(ListView):

    model = Order


class OrderDetailView(DetailView):

    model = Order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders_filtered'] = OrderItem.objects.all()
        return context


@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Game, pk=pk)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(customer=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.items.filter(item__pk=item.pk).exists():
            order_item.quantity += 1
            order_item.save()
            order.increase_total(item)
            messages.info(request, "Added quantity Item")
            return redirect("games:detail", pk=pk)
        else:
            order.items.add(order_item)
            order.increase_total(item)
            messages.info(request, "Item added to your cart")
            return redirect("games:detail", pk=pk)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(customer=request.user, date=ordered_date)
        order.items.add(order_item)
        order.increase_total(item)
        messages.info(request, "Item added to your cart")
        return redirect("games:detail", pk=pk)


@login_required
def remove_from_cart(request, pk):
    # takes an item(game)
    item = get_object_or_404(Game, pk=pk)
    # takes all orders of user which are not ordered
    order_qs = Order.objects.filter(
        customer=request.user,
        ordered=False
    )
    if order_qs.exists():
        # take only the first one
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]

            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                # deletes item
                order_item.delete()
            order.reduce_total(item)
            # in case no more items in order - it is deleted
            if not order.items.exists():
                order.delete()
                return redirect("games:detail", pk=pk)
            messages.info(request, "Item \""+order_item.item.name+"\" remove from your cart")
            return redirect("games:detail", pk=pk)
        else:
            order.reduce_total(item)
            messages.info(request, "This Item not in your cart")
            return redirect("games:detail", pk=pk)
    else:
        #add message doesnt have order
        messages.info(request, "You do not have an Order")
        return redirect("games:detail", pk=pk)


