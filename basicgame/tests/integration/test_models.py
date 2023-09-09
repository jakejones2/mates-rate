from django.test import TestCase
from basicgame.models import Player, Game
from django.core.exceptions import ValidationError


class PlayerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_game = Game.objects.create(
            name="test", cycles=4, boring=False, host="test", progress=0
        )
        Player.objects.create(
            name="Test_1-case", game_id=test_game, points=0, submission=None, votes=None
        )

    def test_name_validation_characters(self):
        obj = Player.objects.create(
            name="@#$%^&*",
            game_id=Game.objects.get(pk=1),
            points=0,
            submission=None,
            votes=None,
        )
        self.assertRaises(ValidationError, obj.full_clean)

    def test_player_string(self):
        player = Player.objects.get(id=1)
        self.assertEqual(str(player), "Test_1-case")

    def test_game_string(self):
        game = Game.objects.get(id=1)
        self.assertEqual(str(game), "test")
