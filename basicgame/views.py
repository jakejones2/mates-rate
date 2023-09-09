import random
from typing import List
from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from basicgame.models import Player, Game
from basicgame.utils import get_players


def home(request):
    hint_list = [
        "Rate your friends in funny categories",
        "You need at least two friends to play",
        "Who scores higher in suffering,<br>me or you?",
        "Knowing the category beforehand is boring",
        "Think outside<br>the box",
        "Which of your parents has the highest agility?",
        "Please start the game already",
        "My improvisation skills are unwavering",
    ]
    category_hints = open("basicgame/resources/categories.txt").readlines()
    character_hints = open("basicgame/resources/characters.txt").readlines()
    ctx = {
        "hint_list": hint_list,
        "category_hints": category_hints,
        "character_hints": character_hints,
    }
    return render(request, "basicgame/home.html", ctx)


class Join(View):
    """
    Page that allows users to join a game via its name. JS drops
    a cookie upon joining the game which contains the game name,
    and the nickname chosen followed by 8 random letters/numbers.
    """

    template_name = "basicgame/join.html"

    def get(self, request) -> HttpResponse:
        """
        Called on a get request to the join page.
        Displays an html form and any validation errors.
        """
        ctx = {"error": ""}
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs) -> HttpResponse:
        """
        Called on a post request to the join page:
        (1) Finds player name, nickname, and game name from the POST request.
        (2) Validates game exists, and sends an error message if not.
        (3) Checks if the player is already in the game, if so, redirects to play view.
            Upon leaving the lobby, player is deleted from db so this is the only
            possible destination. Cookies are remembered by join.js so it is possible
            to rejoin a live game if the user navigates away by mistake.
        (4) Validates game hasn't already started.
        (5) Validates nickname hasn't already been taken.
        (6) Validates nickname is not an empty string.
        (7) Gets or creates the new player.
        (8) Directs to the lobby if game hasn't started.
        (9) Otherwise displays an error.
        """
        player_name: str = request.POST["player-name"]
        player_nickname: str = player_name[:-8]
        game_name: str = request.POST["game-name"].lower().replace("-", "_")
        try:
            game = Game.objects.get(name=game_name)
        except Game.DoesNotExist:
            ctx = {"error": "Game does not exist!"}
            return render(request, self.template_name, ctx)
        player_names: List[str] = [
            player.name for player in Player.objects.filter(game_id=game.pk)
        ]
        player_nicknames = [player[:-8] for player in player_names]
        if player_name in player_names and game.progress:
            return redirect(f"{game.name}/play")
        elif game.progress:
            ctx = {"error": "Game already started!"}
            return render(request, self.template_name, ctx)
        elif player_nickname in player_nicknames:
            ctx = {"error": "Nickname already taken!"}
            return render(request, self.template_name, ctx)
        elif len(player_nickname) <= 0:
            ctx = {"error": "Longer nickname please..."}
            return render(request, self.template_name, ctx)
        else:
            all_player_names = [player.name for player in Player.objects.all()]
            if player_name in all_player_names:
                player = Player.objects.get(name=player_name)
                player.game_id = game
                player.submission = None
                player.votes = None
                player.points = 0
            else:
                player = Player(
                    name=player_name,
                    game_id=game,
                    submission=None,
                    votes=None,
                    points=0,
                )
        player.save()
        if not game.progress:
            return redirect(f"{game.name}/lobby")
        ctx = {"error": "Joining failed, please return to main menu and try again."}
        return render(request, self.template_name, ctx)


class Host(View):
    """
    Page that allows a user to create new game, choose the
    number of cycles, and opt for normal or 'boring' mode.
    Also acts as the join page for the host, creating a player_name
    from a given nickname and dropping a cookie with this name and
    the game name.
    """

    def get(self, request) -> HttpResponse:
        """
        Called on a get request to the host page:
        (1) Generates a random game name based on word-ids.txt
        (2) Checks this game name is not in use.
        (3) Adds some anti-caching headers
        (4) Returns host page showing game name.
        """
        while True:
            n = random.randint(1, 10000)
            fhand = open("basicgame/resources/word-ids.txt")
            word_ids = fhand.readlines()
            word_id = word_ids[n].strip()
            game_names = [game.name for game in Game.objects.all()]
            if not word_id in game_names:
                ctx = {"game_name": word_id}
                break
        response = render(request, "basicgame/host.html", ctx)
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"  # HTTP 1.1.
        response["Pragma"] = "no-cache"  # HTTP 1.0.
        response["Expires"] = "0"  # Proxies.
        return response

    def post(self, request, *args, **kwargs):
        """
        Called on a POST request to the host page:
        (1) Retrieves game name and other data from POST request
        (2) Deletes any existing game and creates a new one.
        (3) Redorects to lobby, which will automatically add
            user to the db. Validation handled on js.
        """
        game_name = request.POST["game-name"]
        boring = request.POST.get("boring", False)
        boring_bool = True if boring else False
        cycles = int(request.POST.get("num-of-cycles", 2))
        cycles = 1 if cycles < 1 else cycles
        if Game.objects.filter(name=game_name):
            Game.objects.get(name=game_name).delete()
        new_game = Game(
            name=game_name,
            cycles=cycles,
            boring=boring_bool,
            host=request.POST["player-name"],
            progress=0,
        )
        new_game.save()
        return redirect(f"{game_name}/lobby")


def lobby(request, game_name: str) -> HttpResponse:
    """
    Lobby allows users to see who is waiting for the game to start,
    and exchange messages with each other. The host can start
    the game from the lobby.

    GET requests are redirected to the join page if the client is
    trying to break in via URL without the right cookie, or when
    the game has already started.
    """
    game = Game.objects.get(name=game_name)
    if not request.COOKIES.get(game_name):
        return redirect("/join")
    if game.progress:
        return redirect("/join")
    return render(
        request, "basicgame/lobby.html", {"game_name": game_name, "host": game.host}
    )


class Play(View):
    """
    Page which shows game content, continiously altered via js
    and websockets.
    """

    def get(self, request, game_name):
        """
        Called on a GET request to the game page.
        Adds game information such as game sequence and players
        to the page for use by js.
        Game should survive refresh.
        """
        category_hints = open("basicgame/resources/categories.txt").readlines()
        character_hints = open("basicgame/resources/characters.txt").readlines()
        host = Game.objects.get(name=game_name).host
        ctx = {
            "players": get_players(game_name),
            "game_name": game_name,
            "host": host,
            "category_hints": category_hints,
            "character_hints": character_hints,
        }
        return render(request, "basicgame/play.html", ctx)


def error(request):
    return HttpResponse("error")
