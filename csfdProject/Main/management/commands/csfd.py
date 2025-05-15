from django.core.management.base import BaseCommand
from Main.movie_scraper import concurently_extract_data
from Main.models import Movie, Actor

"""
    Command to scrap data from CSFD and load them to DB
    Usage: python manage.py csfd
"""

class Command(BaseCommand):
    help = "Scrap data from CSFD and load them to DB"

    def handle(self, *args, **kwargs):
        Movie.objects.all().delete()
        Actor.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Data deleted from DB"))
        
        data = concurently_extract_data(2)

        for movie, herci in data.items(): 
            film, _ = Movie.objects.get_or_create(movie_name=movie)
            herci = data[movie]["actors"]
            for herec in herci:
                actor, _ = Actor.objects.get_or_create(actor_name=herec)
                film.actors.add(actor)
                film.save()

        self.stdout.write(self.style.SUCCESS(f"{len(data)} filmů nahráno do DB"))
