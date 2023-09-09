from django.urls import path
from . import views

app_name = "basicgame"
urlpatterns = [
    path("", views.home, name="home"),
    path("join", views.Join.as_view(), name="join"),
    path("<str:game_name>/lobby", views.lobby, name="lobby"),
    path("host", views.Host.as_view(), name="host"),
    path("error", views.error, name="error"),
    path("<str:game_name>/play", views.Play.as_view(), name="play"),
]
