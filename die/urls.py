"""die URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('django.contrib.auth.urls')),
    
    path('', views.game_list, name='index'),
    
    path('players/', views.player_list, name='player_list'),
    path('players/add/', views.player_add, name='player_add'),
    path('games/', views.game_list, name='game'),
    # see concurrent game details/stats
    path('games/<int:id>/', views.game_detail),
    path('games/<int:id>/<int:big>', views.game_detail_big),
    #path('games/<int:id>/delete', views.game_delete),
    path('games/<int:id>/update', views.update_game),
    path('games/<int:id>/refresh', views.game_refresh),
    # record stats for game
    path('games/<int:id>/stats/record', views.stat_record),
    path('games/<int:id>/stats/delete', views.stat_delete),
    path('leagues/', views.league_list, name='leagues'),
    path('leagues/add/', views.league_add),
    path('leagues/<int:id>/', views.league_detail),
    #path('leagues/<int:id>/delete', views.league_delete),
    path('leagues/<int:id>/teams/add', views.team_add),
    path('leagues/<int:id>/games/add', views.league_game_add),
    path('login/', views.login),
    path('logout/', views.logout),
    path('create/', views.createAdmin),
    path('profile/', views.profile),
    path('privileges/', views.privileges)
]
