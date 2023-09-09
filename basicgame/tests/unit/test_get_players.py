from basicgame.utils import get_players
from basicgame.tests.unit.base import TripleTest
from basicgame.models import Player, Game


class TestGetPlayers(TripleTest):
    """
    Function retrieves all player names from given game id.
    """

    def test_finds_all_three_players(self):
        self.assertEqual(
            get_players(self.test_game.name),
            ["testuser112345678", "testuser212345678", "testuser312345678"],
        )

    def test_finds_players_in_given_game(self):
        self.new_game = Game.objects.create(
            name="testgame2",
            cycles=4,
            boring=False,
            host="testuser112345678",
            progress=1,
        )
        self.user4 = Player.objects.create(
            name="testuser4",
            game_id=self.new_game,
            points=0,
            submission=None,
            votes=None,
        )
        self.user5 = Player.objects.create(
            name="testuser5",
            game_id=self.new_game,
            points=0,
            submission=None,
            votes=None,
        )
        self.assertEqual(
            get_players(self.test_game.name),
            ["testuser112345678", "testuser212345678", "testuser312345678"],
        )
        self.assertEqual(get_players(self.new_game.name), ["testuser4", "testuser5"])
