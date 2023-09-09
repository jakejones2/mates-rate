import json, os, math, logging
from dotenv import load_dotenv
from operator import itemgetter
from typing import List, Dict, Tuple, Optional, Generator
from channels.db import database_sync_to_async  # type: ignore
from google_images_search import GoogleImagesSearch  # type: ignore
from basicgame.models import Game, Player

"""
Selection of utility functions handling game logic. All functions 
can be considered pure aside from their interaction with the 
game database.
"""

load_dotenv()
logger = logging.getLogger(__name__)


@database_sync_to_async
def produce_player_list_html(game_id: int) -> str:
    """
    Takes a game_id, and creates a list of player nicknames that
    are members of this game. Return this list as a html string with
    an enboldened heading.
    """
    player_query_set = Player.objects.filter(game_id=game_id)
    nickname_list: List[str] = [player.name[:-8] for player in player_query_set]
    return "<span style=font-weight:300>players:\n</span>" + "\n".join(nickname_list)


@database_sync_to_async
def get_game_id(game_name: str) -> int:
    """Converts game_name (e.g. panda_button) into its db primary key"""
    return Game.objects.get(name=game_name).pk


def get_player_name_from_cookie(scope: dict, game_name: str) -> Optional[str]:
    """
    Retrieves game cookie ("testgame=testuser12345678") from asgi scope.
    Returns player name from cookie ("testuser12345678").
    """
    if not scope.get("cookies", None):
        return None
    for key, value in scope["cookies"].items():
        if key == game_name:
            return value
    return None


@database_sync_to_async
def ensure_player_in_game_db(player_name: str, game_id: int) -> None:
    """
    Receives player name and game id.
    If the given player name is not in the db with given game_id,
    a new player record is created with the given game_id.
    """
    game = Game.objects.get(pk=game_id)
    player_query_set = Player.objects.filter(game_id=game_id)
    player_name_list: List[str] = [player.name for player in player_query_set]
    if not player_name in player_name_list:
        Player.objects.create(
            name=player_name, game_id=game, points=0, submission=None, votes=None
        )


def get_players(game_name: str) -> List[str]:
    """Takes in a game name, returns a list of player names partaking in this game."""
    game_id: int = Game.objects.get(name=game_name).pk
    player_query_set = Player.objects.filter(game_id=game_id)
    return [player.name for player in player_query_set]


@database_sync_to_async
def get_game_progress(game_id: int) -> Optional[int]:
    """Retrieves game progress"""
    return Game.objects.get(pk=game_id).progress


@database_sync_to_async
def reset_submissions_and_votes(game_id: int) -> None:
    """Sets submissions and votes of all players in particular game to None."""
    for player in Player.objects.filter(game_id=game_id):
        player.submission = None
        player.votes = None
        player.save()


@database_sync_to_async
def remove_player_from_db(player_name: str) -> None:
    """Deletes the given player from the db"""
    Player.objects.filter(name=player_name).delete()


def generate_game_sequence(game_name: str) -> List[str]:
    """
    Takes a game name, and outputs a list of stages representing the game's structure.
    """
    game_sequence = ["lobby"]
    game = Game.objects.get(name=game_name)
    players: List[str] = get_players(game_name)
    total_views: int
    if game.boring:
        total_views = game.cycles * 6 * len(players) + 1
        while True:
            for player in players:
                game_sequence.extend(
                    [
                        f"boring_{player}",
                        "character",
                        "vote",
                        "winner",
                        "results",
                        "leaderboard",
                    ]
                )
            if len(game_sequence) >= total_views:
                game_sequence = game_sequence[:total_views]
                game_sequence.append("finish")
                return game_sequence
    total_views = game.cycles * 5 * len(players) + 1
    while True:
        for player in players:
            game_sequence.extend([player, "vote", "winner", "results", "leaderboard"])
        if len(game_sequence) >= total_views:
            game_sequence = game_sequence[:total_views]
            game_sequence.append("finish")
            return game_sequence


@database_sync_to_async
def generate_game_sequence_async(game_name: str) -> List[str]:
    """Async version of generate_game_sequence"""
    return generate_game_sequence(game_name)


@database_sync_to_async
def collected_and_added_all_input_data(
    player_name: str, field: str, data: str, game_id: int
) -> bool:
    """
    Takes a players name, the database field to be populated, data, and the game_id.
    Function populates database field with data, adding * to duplicates, and then
    checks to see how many other players in the game are yet to submit. Once all
    players have submitted data, the function returns True.
    """
    if field == "submission":
        for player in Player.objects.filter(game_id=game_id):
            if player.submission:
                if player.name == player_name:
                    continue
                elif player.submission.startswith(data):
                    data += "*"
    player = Player.objects.get(name=player_name)
    setattr(player, field, data)
    player.save()
    for player in Player.objects.filter(game_id=game_id):
        if getattr(player, field) == None:
            return False
    return True


@database_sync_to_async
def get_category(game_id: int) -> Optional[str]:
    """
    Finds and returns the category amongst players' 'submission' fields.
    Categories are prefixed by an underscore (e.g. '_speed').
    Category is returned without underscore.
    """
    players = Player.objects.filter(game_id=game_id)
    for player in players:
        if player.submission:
            if player.submission.startswith("_"):
                return player.submission[1:]
    return None


@database_sync_to_async
def create_character_list(game_id: int) -> List[str | None]:
    """Returns a list of characters submitted in the submission round."""
    players = Player.objects.filter(game_id=game_id)
    return [
        player.submission
        for player in players
        if player.submission and not getattr(player, "submission", "").startswith("_")
    ]


@database_sync_to_async
def create_average_score_dict(game_id: int) -> Dict[str, int]:
    """
    Takes game_id, and extracts scores from all relevant players for each
    character. Computes an average and rounds to int. Returns a dictionary
    of characters and integer scores.
    """
    players = Player.objects.filter(game_id=game_id)
    players_voted = [player for player in players if player.votes]
    float_scores: Dict[str, float] = {}
    for player in players_voted:
        if not player.votes:
            continue
        votes: dict = json.loads(player.votes)
        vote_data: List[tuple] = votes["vote"]["voteData"]["characterScores"].items()
        character: str
        score: int
        for character, score in vote_data:
            float_scores[character] = float_scores.get(character, 0) + (
                float(score) / len(players_voted)
            )
    scores: Dict[str, int] = {}
    for character, float_score in float_scores.items():
        scores[character] = round(float_score)
    return scores


@database_sync_to_async
def convert_character_to_player(game_id: int, character: str) -> Optional[str]:
    """
    Takes game_id and a character, searches game for player with this
    character as a submission. Returns the player name that matches.
    """
    players = Player.objects.filter(game_id=game_id)
    for player in players:
        if player.submission == character:
            return player.name[:-8]
    return None


async def calculate_winner(scores: Dict[str, int], game_id: int) -> Dict:
    """
    Takes dictionary of scores and game_id.
    Should find the highest-scoring character, and check for a draw.
    Returns a dictionary of information containing the winner\drawers,
    draw status, the winning character and score if available, and category.
    """
    winner: Tuple[str, int] = max(scores.items(), key=itemgetter(1))
    category: str = await get_category(game_id)
    drawed_characters_list = [
        character for (character, score) in scores.items() if score == winner[1]
    ]
    if len(drawed_characters_list) > 1:
        draw_name_list: List[str] = []
        for character in drawed_characters_list:
            draw_name_list.append(await convert_character_to_player(game_id, character))
        return {"is_draw": True, "drawers_list": draw_name_list}
    name = await convert_character_to_player(game_id, winner[0])
    return {
        "is_draw": False,
        "drawers_list": None,
        "name": name,
        "character": winner[0],
        "category": category,
        "score": winner[1],
    }


def points_generator(num_of_players: int) -> Generator[int, None, None]:
    """
    Takes integer representing the number of players in the game.
    Returns a generator object that yields a sequence of points to be
    allocated to players.
    """
    if num_of_players > 9:
        yield 7
        yield 4
        yield 3
        yield 2
        yield 1
    elif num_of_players > 7:
        yield 5
        yield 3
        yield 2
        yield 1
    elif num_of_players > 5:
        yield 5
        yield 3
        yield 1
    elif num_of_players > 3:
        yield 3
        yield 1
    elif num_of_players > 2:
        yield 1


@database_sync_to_async
def update_player_points(scores: Dict[str, int], game_id: int) -> None:
    """
    Takes scores dictionary and game_id.
    Creates an ordered list of characters and scores from highest to lowest,
    and iterates through this list. On each charater, the function retreives
    the matching player from the db, and increases their points as determined
    by the generator. If there are two or more matching scores in a row
    (i.e, a draw), then these subsequent players recieve the same amount of
    points as the first player and the generator is not called.
    """
    results: List[Tuple[str, int]] = list(scores.items())
    results.sort(key=lambda x: x[1], reverse=True)
    players = Player.objects.filter(game_id=game_id)
    num_of_players = len(players)
    points: Generator[int, None, None] = points_generator(num_of_players)
    previous_score = None
    previous_points = 0
    for character, score in results:
        player = players.get(submission=character)
        if score == previous_score:
            player.points += previous_points
            player.save()
        else:
            try:
                player.points += next(points)
                player.save()
            except StopIteration:
                break
        previous_score = score
        previous_points = player.points


@database_sync_to_async
def create_results_html_table(scores: Dict[str, int], category: str) -> str:
    """
    Takes a dictionary of scores and a category.
    Orders scores in descending order and returns a string representing
    an HTML table. Saves extra js on the front end.
    """
    results: List[Tuple[str, int]] = list(scores.items())
    results.sort(key=lambda x: x[1], reverse=True)
    html = f"<tr><th>character</th><th>{category}</th></tr>"
    for character, score in results:
        html += f"<tr><td>{character}</td><td>{score}</td></tr>"
    return html


@database_sync_to_async
def create_leaderboard_html_table(game_id: int) -> str:
    """
    Takes game id.
    Creates sorted list of players and their current points from db.
    Returns this list as a string representing an HTML table.
    Saves extra js on the front end.
    """
    players = Player.objects.filter(game_id=game_id)
    player_points_list: List[Tuple[str, int]] = [
        (player.name, player.points) for player in players
    ]
    player_points_list.sort(key=lambda x: x[1], reverse=True)
    html = "<tr><th>player</th><th>points</th></tr>"
    for player, points in player_points_list:
        html += f"<tr><td>{player[:-8]}</td><td>{points}</td></tr>"
    return html


@database_sync_to_async
def enough_submissions(game_id: int) -> bool:
    """
    Takes game_id. Iterates through players in game seeing
    if either the category is present and at least one character.
    Returns True if there is enough data to continue the round,
    returns False if the round can't be continued.
    """
    players = Player.objects.filter(game_id=game_id)
    category_present = False
    character_present = False
    for player in players:
        if player.submission:
            if player.submission.startswith("_"):
                category_present = True
            else:
                character_present = True
    return category_present and character_present


@database_sync_to_async
def enough_votes(game_id: int) -> bool:
    """
    Takes game_id. Iterates through players in game to see if
    any votes have been submitted. Returns false if none found.
    """
    players = Player.objects.filter(game_id=game_id)
    for player in players:
        if player.votes:
            return True
    return False


@database_sync_to_async
def advance_progress(game_id, view, game_sequence) -> Optional[int]:
    """
    Increments game progress to index of given view in game sequence.
    If this view is already reached, or if the view is not next in line,
    nothing changes. Helps prevent the round being incremented twice when
    network is slow.
    """
    game = Game.objects.get(pk=game_id)
    current_progress = game.progress
    if view == "submission":
        latter_views = ["character", "vote", "winner", "results", "leaderboard"]
        if not game_sequence[current_progress + 1] in latter_views:
            game.progress += 1
            game.save()
            return game.progress
    elif view == game_sequence[current_progress + 1]:
        game.progress += 1
        game.save()
        return game.progress
    return current_progress


@database_sync_to_async
def change_game_progress(game_id: int, progress: int) -> int:
    """
    Updates the game progress to the given progress integer.
    Returns the new progress value.
    """
    game = Game.objects.get(id=game_id)
    game.progress = progress
    game.save()
    return game.progress


def get_total_game_views(game_id: int) -> int:
    """
    Takes game_id.
    Calculates the total number of stages in a full game based on
    the number of cycles, number of players and whether the game
    is in boring mode or not.
    Returns total number of stages as an integer.
    Does not include the 'finish' view.
    """
    num_of_players = len(Player.objects.filter(game_id=game_id))
    game = Game.objects.get(pk=game_id)
    if game.boring:
        return 1 + game.cycles * num_of_players * 6
    return 1 + game.cycles * num_of_players * 5


async def next_round(game_id: int, game_sequence: List[str]) -> Optional[int]:
    """
    Takes the game_id and game_sequence.
    Retrieves current game progress, and finds the round number of the
    next sumbission view, or the next finishing view. Returns the index
    of this round number.
    """
    progress: int = await get_game_progress(game_id)
    view: str
    for index, view in enumerate(game_sequence):
        if index <= progress:
            continue
        if not view in ["character", "vote", "winner", "results", "leaderboard"]:
            return index
    return None


@database_sync_to_async
def delete_game_if_finished(game_id: int) -> bool:
    """
    If the game has finished, the related Game and Player db
    records are deleted.
    """
    game = Game.objects.get(id=game_id)
    if game.progress >= get_total_game_views(game_id):
        Player.objects.filter(game_id=game_id).delete()
        game.delete()
        return True
    return False


@database_sync_to_async
def add_category(game_id: int, player_name: str, category: str) -> None:
    """
    Takes game id, player name and category.
    Finds player with correct game id and name, and adds category in the
    submission field.
    """
    players = Player.objects.filter(game_id=game_id)
    player = players.get(name=player_name)
    player.submission = category
    player.save()


@database_sync_to_async
def is_boring(game_id: int) -> bool:
    """
    Takes game id.
    Returns True if game is in boring mode, otherwise False.
    """
    game = Game.objects.get(pk=game_id)
    return game.boring


@database_sync_to_async
def get_category_submitter(game_id) -> Optional[str]:
    """
    Takes game id.
    Finds the player with matching game id who has recently
    submitted a category (categories are preceded by '_').
    Returns this player's name.
    """
    players = Player.objects.filter(game_id=game_id)
    for player in players:
        if player.submission:
            if player.submission.startswith("_"):
                return player.name
    return None


def find_image(winner) -> Optional[str]:
    """
    Uses GoogleImagesApi to find an image online for the winner.
    Returns the url as a string.
    """
    if winner["is_draw"]:
        return None
    search_params = {
        "q": f"{winner['character']} face",
        "num": 1,
        "safe": "active",
        "imgSize": "medium",
    }

    gis = GoogleImagesSearch(os.getenv("GCS_CX"), os.getenv("GCS_DEVELOPER_KEY"))

    try:
        gis.search(
            search_params=search_params,
        )
        for image in gis.results():
            return image.url
    # if we use up API image allowance for a day
    # an error will presumably be thrown
    except Exception as err:
        logger.warning(err, "image search may have failed - check api quota")
    return None


@database_sync_to_async
def generate_progress_string(game_id) -> str:
    """
    Receives game id, returns a string showing game progress.
    """
    game = Game.objects.get(pk=game_id)
    players = Player.objects.filter(game_id=game.pk)
    if game.boring:
        current_round = math.floor((game.progress - 1) / 6) + 1
        total_rounds = game.cycles * len(players)
        return f"Round {current_round} of {total_rounds}"
    current_round = math.floor((game.progress - 1) / 5) + 1
    total_rounds = game.cycles * len(players)
    return f"Round {current_round} of {total_rounds}"


async def generate_round_json(round_type, game_id, next=None) -> str:
    """
    Generates a json string for each round of the game.
    Does not update the game or player database.
    """
    if round_type == "character":
        return json.dumps(
            {
                "progress": await get_game_progress(game_id),
                "view": "character",
                "category": await get_category(game_id),
                "categoryPicker": await get_category_submitter(game_id),
            }
        )
    elif round_type == "vote":
        return json.dumps(
            {
                "progress": await get_game_progress(game_id),
                "view": "vote",
                "poll": await create_character_list(game_id),
                "category": await get_category(game_id),
            }
        )

    if round_type == "winner":
        scores: Dict[str, int] = await create_average_score_dict(game_id)
        winner = await calculate_winner(scores, game_id)
        return json.dumps(
            {
                "progress": await get_game_progress(game_id),
                "view": "winner",
                "winner": winner,
                "image": find_image(winner),
                "nextViewAt": next,
            }
        )
    elif round_type == "results":
        scores = await create_average_score_dict(game_id)
        category: str = await get_category(game_id)
        return json.dumps(
            {
                "progress": await get_game_progress(game_id),
                "view": "results",
                "resultsHtmlTable": await create_results_html_table(scores, category),
                "nextViewAt": next,
            }
        )
    elif round_type == "leaderboard":
        return json.dumps(
            {
                "progress": await get_game_progress(game_id),
                "view": "leaderboard",
                "leaderboardHtmlTable": await create_leaderboard_html_table(game_id),
                "nextViewAt": next,
            }
        )
    else:
        return json.dumps(
            {
                "progress": await get_game_progress(game_id),
                "view": round_type,
                "round": await generate_progress_string(game_id),
            }
        )
