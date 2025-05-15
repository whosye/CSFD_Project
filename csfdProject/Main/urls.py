from django.contrib import admin
from django.urls import path,include
from .views import index, search_result, movie_detail, actor_detail

app_name = 'Main'
urlpatterns = [
    path('', index, name='index'),
    path('search_result/', search_result, name='search_result'),
    path('movie_detail/<int:movie_id>/', movie_detail, name='movie_detail'),
    path('actor_detail/<int:actor_id>/', actor_detail, name='actor_detail'),
]
