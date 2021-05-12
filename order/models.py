from django.db import models
from django.conf import settings
from django.db.models import Sum

from games.models import Game


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    total = models.FloatField(default=0)
    items = models.ManyToManyField('OrderItem')
    ordered = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def increase_total(self, order_item):
        self.total += order_item.price
        self.save()

    def reduce_total(self, order_item):
        self.total -= order_item.price
        self.save()

    def destroy_order(self):
        for item in self.items.all():
            item.item.quantity_available += item.quantity

    def __str__(self):
        return f"{self.customer.username}'s order - {'ordered' if self.ordered else 'NOT ordered'}"


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Game, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def adding_game_to_cart(self):
        self.item.quantity_available -= 1
        self.item.save()

    def remove_game_from_cart(self):
        self.item.quantity_available += 1
        self.item.save()

    def __str__(self):
        return f"{self.quantity} piece(s) of {self.item.name} - {'ordered' if self.ordered else 'NOT ordered'}"
