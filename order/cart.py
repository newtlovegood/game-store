import json

from order.models import Order
from games.models import Game


class Cart:

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if 'cart' not in request.session:
            cart = self.session['cart'] = {}
        self.cart = cart
        if not self.cart:
            try:
                Order.objects.get(ordered=False).delete()
            except Order.DoesNotExist:
                pass

    def add(self, item, qty=0):

        item_id = str(item.id)
        if item_id not in self.cart:
            self.cart[item_id] = {'item_price': item.price, 'qty': int(qty)}
        else:
            new_qty = self.cart[item_id]['qty'] + qty
            self.cart[item_id] = {'item_price': item.price, 'qty': int(new_qty)}
        self.session.modified = True

    def remove(self, item, qty=1):

        item_id = str(item.id)
        new_qty = self.cart[item_id]['qty'] - qty
        self.cart[item_id] = {'item_price': item.price, 'qty': int(new_qty)}
        self.session.modified = True

    def delete(self, item):

        item_id = str(item.id)
        if item.id not in self.cart:
            del self.cart[item_id]

        self.session.modified = True

    def clear(self):
        self.cart.clear()
        self.session.modified = True

    def __len__(self):
        return sum(item['qty'] for item in self.cart.values())


