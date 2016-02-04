__author__ = 'wwagner'

from Thud import ThudServerDjango
from django.conf.urls import url
from django.views.generic import TemplateView

urlpatterns = [
        url(r"^$", TemplateView.as_view(template_name="Thud/thud.html"), ),
        url(r"^getgamebyid/([a-zA-Z0-9]+)", ThudServerDjango.get_game_by_id_handler),
        url(r"^version", ThudServerDjango.get_version),
        url(r"^start", ThudServerDjango.StartGameWithPlayers),
        url(r"^move", ThudServerDjango.ExecuteMove),
        url(r"^move/validate", ThudServerDjango.ValidateMove),
        url(r"^game", ThudServerDjango.GetBoardState),
        url(r"^save", ThudServerDjango.SaveGame),
        url(r"^load", ThudServerDjango.LoadGame),
        # url(r"^match/([A-Za-z0-9]+)", DjangoThudServer.PlayerConnection),
    ]