from basicgame.tests.unit.base import TripleTest, hash_database
from basicgame.utils import generate_game_sequence


class TestGenerateGameSequence(TripleTest):
    """
    Takes game name, produces a list of strings representing the game sequence.
    Should have no side effects.
    """

    def test_generate_game_sequence_basic(self):
        """
        Should return correct string, ending with 'finish', when boring = False.
        """
        self.assertEqual(
            generate_game_sequence(self.test_game.name),
            [
                "lobby",
                "testuser112345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "testuser212345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "testuser312345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "testuser112345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "testuser212345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "testuser312345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "testuser112345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "testuser212345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "testuser312345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "testuser112345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "testuser212345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "testuser312345678",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "finish",
            ],
        )

    def test_generate_game_sequence_boring(self):
        """
        Should produce correct sequence in boring mode
        """
        self.test_game.boring = True
        self.test_game.cycles = 2
        self.test_game.save()
        self.assertEqual(
            generate_game_sequence(self.test_game.name),
            [
                "lobby",
                "boring_testuser112345678",
                "character",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "boring_testuser212345678",
                "character",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "boring_testuser312345678",
                "character",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "boring_testuser112345678",
                "character",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "boring_testuser212345678",
                "character",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "boring_testuser312345678",
                "character",
                "vote",
                "winner",
                "results",
                "leaderboard",
                "finish",
            ],
        )

    def test_generate_game_sequence_should_not_alter_database(self):
        """
        Test database hash is the same before and after calling the function.
        """
        hash1 = hash_database()
        generate_game_sequence(self.test_game.name)
        hash2 = hash_database()
        self.assertEqual(hash1, hash2)
