from django.urls import reverse_lazy
from django.shortcuts import get_list_or_404
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView, ListView
from django.views.generic.edit import ModelFormMixin, FormMixin
from django.contrib.auth.mixins import UserPassesTestMixin

from games.models import Game
from games.forms import GameCreateForm, GameSearchForm
from comment.forms import CommentForm


class HomePageView(FormMixin, TemplateView):

    template_name = 'index.html'

    form_class = GameSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['games'] = Game.objects.all()
        return context


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

    # def post(self, request, *args, **kwargs):
    #     form = self.get_form(self.form_class)
    #     print(request.FILES)
    #     if form.is_valid():
    #         form.save()
    #         return self.form_valid(form)
    #     else:
    #         return self.form_invalid(form)

    def test_func(self):
        return self.request.user.groups.filter(name='managers').exists()


class GameDeleteView(UserPassesTestMixin, DeleteView):

    model = Game
    success_url = reverse_lazy('games:home')

    def test_func(self):
        return self.request.user.groups.filter(name='managers').exists()


class GameFilterView(TemplateView):

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['games'] = get_list_or_404(Game.objects.all().filter(genre__name__icontains=kwargs.get('slug')))
        return context


class GameSearchView(ListView):

    template_name = 'index.html'
    model = Game

    # to match THIS queryset with HOMEVIEW's (not to repeat some code in template)
    context_object_name = 'games'

    def get_queryset(self):
        # to GET VALUE from search form
        query = self.request.GET.get('q')
        games = get_list_or_404(Game.objects.filter(name__icontains=query))
        return games



