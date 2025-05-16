from django.core.management.base import BaseCommand
from Main.movie_scraper import extract_all_data
from Main.models import Movie, Actor
class Command(BaseCommand):
    """
        Delete all data from DB and scrap data from CSFD
        Usage: python manage.py csfd --pages 3 --seq True
    """
    help = "Scrap data from CSFD and load them to DB"

    def add_arguments(self, parser):
        parser.add_argument('--pages', type=int, default=3, help='Number of pages to scrap')
        parser.add_argument('--seq', type=bool, default=False, help='Scrap same amount of pages sequentially to compare the time')

    def handle(self, *args, **kwargs):
        Movie.objects.all().delete()
        Actor.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Data deleted from DB"))
        self.stdout.write(self.style.SUCCESS(f"Starting to scrap {kwargs['pages']} pages from CSFD"))

        try:
            data = extract_all_data(pages=kwargs['pages'], seq=kwargs['seq'])
            for movie, herci in data.items(): 
                film, _ = Movie.objects.get_or_create(movie_name=movie)
                herci = data[movie]
                for herec in herci:
                    actor, _ = Actor.objects.get_or_create(actor_name=herec)
                    film.actors.add(actor)

            self.stdout.write(self.style.SUCCESS(f"Number of movies {len(data)} loaded to DB"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            return
