from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"wss/lobby/(?P<game_name>\w+)/$", consumers.LobbyConsumer.as_asgi()),
    re_path(r"wss/(?P<game_name>\w+)/play/$", consumers.GameConsumer.as_asgi()),
    re_path(r"ws/lobby/(?P<game_name>\w+)/$", consumers.LobbyConsumer.as_asgi()),
    re_path(r"ws/(?P<game_name>\w+)/play/$", consumers.GameConsumer.as_asgi()),
]
