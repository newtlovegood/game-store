from django.urls import reverse_lazy
from django.shortcuts import get_list_or_404, render
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView, ListView
from django.views.generic.edit import ModelFormMixin, FormMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q

from games.models import Game
from games.forms import GameCreateForm, GameSearchForm, GameFilterForm
from comment.forms import CommentForm


class HomePageView(TemplateView):

    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        form_search = GameSearchForm()
        form_filter = GameFilterForm()
        games = Game.objects.all()
        context = {'form_search': form_search, 'form_filter': form_filter, 'games': games}
        return render(request, self.template_name, context)


class SingleGameView(ModelFormMixin, DetailView):

    model = Game

    form_class = CommentForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        # if not request.user.is_authenticated:
        #     return HttpResponseForbidden()
        # self.object = self.get_object()

        # ADDING GAME AND USER FIELDS TO FORM
        form = self.get_form()
        form.instance.game = Game.objects.filter(id=self.kwargs.get('pk'))[0]
        form.instance.username = request.user
        # parent fields to fill with Javascript
        form.save()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, **kwargs):
        return super().form_valid(form)


class GameCreateView(UserPassesTestMixin, CreateView):

    template_name = 'games/game_form.html'
    form_class = GameCreateForm
    model = Game

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.groups.filter(name='managers').exists()


class GameEditView(UserPassesTestMixin, UpdateView):

    model = Game
    fields = '__all__'
    template_name_suffix = '_update_form'

    def test_func(self):
        return self.request.user.groups.filter(name='managers').exists()

    def form_valid(self, form):
        print(form.data)
        return super().form_valid(form)


class GameDeleteView(UserPassesTestMixin, DeleteView):

    model = Game
    success_url = reverse_lazy('games:home')

    def test_func(self):
        return self.request.user.groups.filter(name='managers').exists()


class GameFilterView(ListView):

    template_name = 'index.html'
    model = Game
    context_object_name = 'games'

    def get(self, request, pk=None, *args, **kwargs):
        # init forms
        form_search = GameSearchForm()
        form_filter = GameFilterForm()
        # get filtered games

        genre_query = self.request.GET.getlist('filter-f')
        games_query = Game.objects.all()
        for genre in genre_query:
            games_query = games_query.filter(genre=genre)

        if pk:
            games_query = get_list_or_404(games_query.filter(genre=pk))

        context = {'form_search': form_search, 'form_filter': form_filter, 'games': games_query}
        return render(request, self.template_name, context)


class GameSearchView(ListView):

    template_name = 'index.html'
    model = Game

    # to match THIS queryset with HOMEVIEW's (not to repeat some code in template)
    context_object_name = 'games'

    def get(self, request, *args, **kwargs):
        # init forms
        form_search = GameSearchForm()
        form_filter = GameFilterForm()
        # get filtered games
        query = self.request.GET.get('q')
        games = Game.objects.filter(name__icontains=query)

        context = {'form_search': form_search, 'form_filter': form_filter, 'games': games}
        return render(request, self.template_name, context)



