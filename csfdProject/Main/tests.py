from django.test import TestCase
from .models import Movie, Actor
from django.core.management import call_command
from Main.movie_scraper import extract_all_data
import os 
from unittest.mock import patch, Mock
class Test_Model(TestCase):

    def setUp(self):
        # definice dat
        self.actor_groups = [
            ["Pepa0", "Jirka Pomeje0", "Baba Pod Korenem0", "Martin Pohl0"],
            ["Pepa1", "Jirka Pomeje1", "Baba Pod Korenem1", "Martin Pohl1"],
            ["Pepa2", "Jirka Pomeje2", "Baba Pod Korenem2", "Martin Pohl2"],
        ]
        self.movie_names = ["Babovresky", "Snowboardaci", "Rambo"]

        self.movies = []
        # create movies
        for name in self.movie_names:
            self.movies.append(Movie.objects.create(movie_name=name))

        # assign actors to movies
        for movie, actor_list in zip(self.movies, self.actor_groups):
            for actor_name in actor_list:
                actor = Actor.objects.create(actor_name=actor_name)
                movie.actors.add(actor)

    def test_movie_creation(self):
        # test if the movies are created
        for name in self.movie_names:
            with self.subTest(name=name):
                movie = Movie.objects.get(movie_name=name)
                self.assertEqual(movie.movie_name, name)

    def test_actor_creation(self):
        # test actors creation
        for actor_list in self.actor_groups:
            for actor_name in actor_list:
                with self.subTest(actor_name=actor_name):
                    actor = Actor.objects.get(actor_name=actor_name)
                    self.assertEqual(actor.actor_name, actor_name)

    def test_movie_actor_relationship(self):
        # test M2M relationship
        for indx, movie in enumerate(self.movie_names):
            with self.subTest(movie=movie):
                movie_instance = Movie.objects.get(movie_name=movie)
                actors = movie_instance.actors.all()
                actors = [actor.actor_name for actor in actors]
                self.assertEqual(actors,self.actor_groups[indx])

class TestMockedScraper(TestCase):
    def load_html(self, filename):
        # HTML loader
        path = os.path.join(os.path.dirname(__file__), "test_data", filename)
        with open(path, encoding="utf-8") as f:
            return f.read()

    @patch("requests.get")
    def test_scraping(self, mock_get):
        # get fake HTML
        fake_movies_html = self.load_html("movies.html")
        fake_actors_html = self.load_html("actors.html")

        # mocking the requests.get method
        def side_effect(url, *args, **kwargs):
            mock_resp = Mock()
            if "nejlepsi" in url:
                mock_resp.text = fake_movies_html
            else:
                mock_resp.text = fake_actors_html
            return mock_resp
        
        # mocking the response of requests.get
        mock_get.side_effect = side_effect

        # get data
        data = extract_all_data(pages=1, seq=False)

        # assertions
        self.assertEqual(len(data), 2)
        self.assertIn("Film 1", data)
        self.assertIn("Herec Jeden", data["Film 1"])
        self.assertIn("Film 2", data)
        self.assertEqual(data["Film 2"], ["Herec Jeden", "Herec Dva"])
class TestCSFDCommand(TestCase):
    @patch("Main.management.commands.csfd.extract_all_data")
    def test_csfd_command_creates_movies_and_actors(self, mock_extract):
        # fake data
        mock_extract.return_value = {
            "Film 1": ["Herec Jeden", "Herec Dva"],
            "Film 2": ["Herec Tři"]
        }

        # run cmnd
        call_command("csfd", pages=1, seq=False)

        self.assertEqual(Movie.objects.count(), 2)
        self.assertEqual(Actor.objects.count(), 3)

        film1 = Movie.objects.get(movie_name="Film 1")
        self.assertEqual(film1.actors.count(), 2)

        film2 = Movie.objects.get(movie_name="Film 2")
        self.assertEqual(film2.actors.count(), 1)

        # check calling with correct arguments
        mock_extract.assert_called_once_with(pages=1, seq=False)