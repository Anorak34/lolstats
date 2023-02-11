from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('stats/', views.champ_stats, name='champ_stats'),
    path('multisearch/', views.multisearch, name='multisearch'),
    path('player/<str:region>/<str:player_name>/', views.player_stats, name='player_stats'),
    path('player/', views.player, name='player'),
]