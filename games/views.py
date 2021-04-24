from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView

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


class GameCreateView(CreateView):

    model = Game
    fields = ['name', 'price', 'genre', 'description']


class GameEditView(UpdateView):

    model = Game
    fields = ['name', 'price', 'genre', 'description']
    template_name_suffix = '_update_form'


class GameDeleteView(DeleteView):

    model = Game
    success_url = reverse_lazy('games:home')
