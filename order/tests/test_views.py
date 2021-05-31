from django.test import TestCase
from django.shortcuts import reverse

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from order.models import Order, OrderItem
from games.models import Game


