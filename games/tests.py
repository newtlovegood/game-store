from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model, authenticate

from .models import Game, Genre

## TEST MODELS
genres = [

        ('Strategy', 'Strategy'),
        ('RPG', 'RPG'),
        ('Sports', 'Sports'),
        ('Races/Rally', 'Races/Rally'),
        ('Races/Arcade', 'Races/Arcade'),
        ('Races/Formula', 'Races/Formula'),
        ('Races/Off-Road', 'Races/Off-Road'),
        ('Action/FPS', 'Action/FPS'),
        ('Action/TPS', 'Action/TPS'),
        ('Action/Misc', 'Action/Misc'),
        ('Adventure', 'Adventure'),
        ('Puzzle/Skills', 'Puzzle/Skills'),
        ('Other', 'Other'),
    ]


class GameModelTest(TestCase):

    def setUp(self):
        # get Group created
        Group.objects.create(name='managers')
        # get user created
        User = get_user_model()
        test_user = User.objects.create_user(username='testuser1', email='test@email.com', password='password')
        # add user to managers
        managers_grp = Group.objects.get(name='managers')
        managers_grp.user_set.add(test_user)
        managers_grp.save()
        # login
        response = self.client.post(reverse('account_login'), {'login': 'test@email.com', 'password': 'password'}, follow=False)
        # get genre
        self.genre1 = Genre.objects.all()[0]
        self.genre2 = Genre.objects.all()[1]
        # create game object
        self.game = Game.objects.create(
            name='TestGame',
            price=10.99,
            description='Test Game description',
            quantity_available=100
        )
        self.game.genre.set([self.genre1, self.genre2])

    def test_genre_listing(self):
        self.assertEqual(self.genre1.name, 'Strategy')
        self.assertEqual(self.genre2.name, 'RPG')

    def test_game_listing(self):
        self.assertEqual(self.game.name, 'TestGame')
        self.assertEqual(self.game.price, 10.99)
        self.assertEqual(self.game.description, 'Test Game description')
        self.assertEqual(self.game.quantity_available, 100)

    def test_game_has_genre(self):
        self.assertEqual(self.game.genre.count(), 2)

    def test_get_absolute_url(self):
        response = self.client.get(self.game.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_if_qty_is_enough(self):
        self.assertTrue(self.game.is_qty_enough(100))
        self.assertFalse(self.game.is_qty_enough(101))

    def test_game_str_method(self):
        self.assertEqual(str(self.game), 'TestGame')

    def test_genre_str_method(self):
        self.assertEqual(str(self.genre1), 'Strategy')

    # test views

    def test_home_page(self):
        response = self.client.get(reverse('games:home'))
        self.assertTemplateUsed(response, 'index.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Genre')

    def test_single_game_view(self):
        response = self.client.get(self.game.get_absolute_url())
        self.assertTemplateUsed(response, 'games/game_detail.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TestGame')

    def test_create_game_view(self):
        game_post_data = {
            'name': 'NewGameName',
            'price': 99.99,
            'description': 'New description',
            'quantity_available': 111,
        }
        get_response = self.client.get(reverse('games:add'))
        response = self.client.post(reverse('games:add'), game_post_data, follow=False)
        # check if game was created
        new_game = Game.objects.get(name='NewGameName')
        self.assertTrue(new_game)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, new_game.get_absolute_url())
        self.assertTemplateUsed(get_response, 'games/game_form.html')

    def test_edit_game_view(self):
        game_post_data = {
            'name': 'UpdatedGameName',
            'price': 99.99,
            'description': 'Updated description',
            'quantity_available': 111,
        }
        existing_game_url = reverse('games:edit', kwargs={'pk': self.game.id})
        get_response = self.client.get(existing_game_url)
        response = self.client.post(existing_game_url, game_post_data)
        # check if game was edited
        updated_game = Game.objects.get(name='UpdatedGameName')
        self.assertTrue(updated_game)
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, updated_game.get_absolute_url())
        self.assertTemplateUsed(get_response, 'games/game_update_form.html')

    def test_delete_game_view(self):
        existing_game_url = reverse('games:delete', kwargs={'pk': self.game.id})
        get_response = self.client.get(existing_game_url)
        response = self.client.post(existing_game_url)
        # check if game deleted
        self.assertFalse(Game.objects.all())
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('games:home'))
        self.assertTemplateUsed(get_response, 'games/game_confirm_delete.html')

    def test_game_filter_view(self):
        # create some additional games
        g1 = Game.objects.create(name='test1', description='test1')
        g2 = Game.objects.create(name='test2', description='test2')
        # add genres
        g1.genre.add(self.genre1)
        g2.genre.add(self.genre2)

        response_two_genres = self.client.get(reverse('games:filter'), {'filter-f': [
                                                                    self.genre1.id,
                                                                    self.genre2.id
                                                                ]})
        self.assertEqual(response_two_genres.context['games'][0], Game.objects.filter(genre=self.genre1.id).filter(genre=self.genre2.id)[0])
        self.assertTrue(response_two_genres.context['form_filter'])
        self.assertTemplateUsed(response_two_genres, 'index.html')
        self.assertEqual(response_two_genres.status_code, 200)

        response_one_genre = self.client.get(reverse('games:filter'), {'filter-f': self.genre1.id})
        self.assertEqual(response_one_genre.context['games'][0],
                         Game.objects.filter(genre=self.genre1.id)[0])
        self.assertEqual(response_one_genre.context['games'][1],
                         Game.objects.filter(genre=self.genre1.id)[1])
        self.assertTrue(response_one_genre.context['form_filter'])
        self.assertTemplateUsed(response_one_genre, 'index.html')
        self.assertEqual(response_one_genre.status_code, 200)

        response_pk = self.client.get(reverse('games:filter', kwargs={'pk': self.genre1.pk}))
        self.assertEqual(response_pk.context['games'][0], Game.objects.filter(genre=self.genre1.id)[0])
        self.assertTrue(response_pk.context['form_filter'])
        self.assertTemplateUsed(response_pk, 'index.html')
        self.assertEqual(response_pk.status_code, 200)

    def test_search_game_view(self):
        # create some additional games
        g1 = Game.objects.create(name='test1', description='test1')
        g2 = Game.objects.create(name='test2', description='test2')

        response = self.client.get(reverse('games:search'), {'q': 'test'})
        self.assertEqual(response.context['games'][0], self.game)
        self.assertEqual(response.context['games'][1], g1)
        self.assertEqual(response.context['games'][2], g2)
        self.assertTrue(response.context['form_search'])
        self.assertTemplateUsed(response, 'index.html')
        self.assertEqual(response.status_code, 200)

        response_wrong = self.client.get(reverse('games:search'), {'q': 'missing'})
        self.assertFalse(response_wrong.context['games'])
