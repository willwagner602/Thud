__author__ = 'wwagner'

from Thud import DjangoThudServer
from django.conf.urls import url

urlpatterns = [
        url(r"^getgamebyid/([0-9]+)", DjangoThudServer.get_game_by_id_handler),
        url(r"^version", DjangoThudServer.get_version),
        url(r"^start", DjangoThudServer.StartGameWithPlayers),
        url(r"^move", DjangoThudServer.ExecuteMove),
        url(r"^move/validate", DjangoThudServer.ValidateMove),
        url(r"^game", DjangoThudServer.GetBoardState),
        url(r"^save", DjangoThudServer.SaveGame),
        url(r"^load", DjangoThudServer.LoadGame),
        # url(r"^match/([A-Za-z0-9]+)", DjangoThudServer.PlayerConnection),
    ]