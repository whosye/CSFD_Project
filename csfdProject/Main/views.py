from django.shortcuts import render
from django.http import JsonResponse
from .models import Movie, Actor
from rapidfuzz import fuzz

def index(request):
    return render(request, 'Main/index.html')


def search_result(request):
    """
    input: film_name
    output: render html with list of movies and actors
    """
    query = request.GET.get('film_name')
    all_movies = Movie.objects.all()
    actors, matched_movies, threshold, movies_to_query = [], [], 50, 10
    for movie in all_movies:
        similarity = fuzz.partial_ratio(query.lower(), movie.movie_name.lower())
        if similarity > threshold:
            matched_movies.append(movie)
            for actor in movie.actors.all():
                if actor not in actors:
                    actors.append(actor)
            # limit fulfiled
            if len(matched_movies) > movies_to_query:
                break
    
    data = {'matched_movies': matched_movies,'actors': actors}
    return render(request, 'Main/search_result.html', data)

def movie_detail(request, movie_id: int):
    """
    input: movie_id
    output: render html with movie object and list of actors
    """
    movie = Movie.objects.get(id=movie_id)
    actors = movie.actors.all()
    data = {'movie': movie, 'actors': actors}
    return render(request, 'Main/movie_detail.html', data)

def actor_detail(request, actor_id: int):
    """
    input: actor_id
    output: render html with actor object and list of movies
    """
    actor = Actor.objects.get(id=actor_id)
    movies = actor.movies.all()
    data = {'actor': actor, 'movies': movies}
    return render(request, 'Main/actor_detail.html', data)
