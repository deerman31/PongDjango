from django.urls import re_path
from .ponggame.tournament.tournament_consumer import TournamentConsumer
from .ponggame.single_game.single_game_consumer import SingleGameConsumer
from .rock_paper_scissors.rock_paper_scissors_consumber import RockPaperScissorsConsumer

websocket_urlpatterns = [
    re_path(r'^ws/single_game/$', SingleGameConsumer.as_asgi()),
    re_path(r'^ws/tournament/$', TournamentConsumer.as_asgi()),
    re_path(r'^ws/rock_paper_scissors/$', RockPaperScissorsConsumer.as_asgi()),
]
