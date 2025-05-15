from django.db import models

class Movie(models.Model):
    movie_name = models.CharField(max_length=255)

    def __str__(self):
        return self.movie_name + " hraji: " + self.actors.all()[0].actor_name if self.actors.all() else "Bez herců"
class Actor(models.Model):
    actor_name = models.CharField(max_length=255)
    movies = models.ManyToManyField(Movie, related_name='actors')

    def __str__(self):
        return self.actor_name  