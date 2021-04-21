from django.utils import timezone

from django.shortcuts import render
from django.views.generic import TemplateView, DetailView

from games.models import Game


class HomePageView(TemplateView):

    template_name = 'index.html'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['games'] = Game.objects.all()[:5]
        return context


class SingleGameView(DetailView):

    model = Game

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

