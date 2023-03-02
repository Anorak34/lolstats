from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('multisearch/', views.multisearch, name='multisearch'),
    path('player/', views.player, name='player'),
    path('player/<str:region>/<str:player_name>/', views.player_stats, name='player_stats'),
    path('player/<str:region>/<str:player_name>/live/', views.player_live, name='player_live'),
]

