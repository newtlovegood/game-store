from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView

from games.models import Game
from games.forms import GameCreateForm


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

    template_name = 'games/game_form.html'
    form_class = GameCreateForm
    model = Game

    def form_valid(self, form):
        print(form.data)
        return super().form_valid(form)


class GameEditView(UpdateView):

    model = Game
    fields = ['name', 'price', 'genre', 'description']
    template_name_suffix = '_update_form'


class GameDeleteView(DeleteView):

    model = Game
    success_url = reverse_lazy('games:home')


class GameFilterView(TemplateView):

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(kwargs.get('slug'))
        context['games'] = Game.objects.all().filter(genre=kwargs.get('slug'))
        return context

