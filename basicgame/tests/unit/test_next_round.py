from basicgame.utils import next_round
from basicgame.tests.unit.base import TripleTest, hash_database_async


class TestNextRound(TripleTest):
    """
    Takes the game_id and game_sequence.
    Retrieves current game progress, and finds the round number of the
    next sumbission view, or the next finishing view. Returns the index
    of this round number. Has no side effects.
    """

    async def test_works_round_1_boring_false(self):
        await self.set_game_progress(0)
        output = await next_round(self.test_game.pk, game_sequence.copy())
        self.assertEqual(output, 5)
        await self.set_game_progress(4)
        output = await next_round(self.test_game.pk, game_sequence.copy())
        self.assertEqual(output, 5)

    async def test_works_round_2_boring_false(self):
        await self.set_game_progress(5)
        output = await next_round(self.test_game.pk, game_sequence.copy())
        self.assertEqual(output, 10)
        await self.set_game_progress(6)
        output = await next_round(self.test_game.pk, game_sequence.copy())
        self.assertEqual(output, 10)

    async def test_works_on_winner(self):
        await self.set_game_progress(59)
        output = await next_round(self.test_game.pk, game_sequence.copy())
        self.assertEqual(output, 60)

    async def test_works_boring_true(self):
        await self.set_game_progress(0)
        output = await next_round(self.test_game.pk, game_sequence_boring.copy())
        self.assertEqual(output, 6)
        await self.set_game_progress(4)
        output = await next_round(self.test_game.pk, game_sequence_boring.copy())
        self.assertEqual(output, 6)
        await self.set_game_progress(13)
        output = await next_round(self.test_game.pk, game_sequence_boring.copy())
        self.assertEqual(output, 18)

    async def test_does_not_mutate_game_sequence(self):
        game_sequence_copy = game_sequence.copy()
        await self.set_game_progress(6)
        await next_round(self.test_game.pk, game_sequence_copy)
        self.assertEqual(game_sequence_copy, game_sequence.copy())
        game_sequence_boring_copy = game_sequence_boring.copy()
        await self.set_game_progress(17)
        await next_round(self.test_game.pk, game_sequence_boring_copy)
        self.assertEqual(game_sequence_boring_copy, game_sequence_boring.copy())

    async def test_does_not_modify_db(self):
        await self.set_game_progress(10)
        hash1 = await hash_database_async()
        await next_round(self.test_game.pk, game_sequence.copy())
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)
        # boring mode
        await self.set_game_progress(17)
        hash3 = await hash_database_async()
        await next_round(self.test_game.pk, game_sequence_boring.copy())
        hash4 = await hash_database_async()
        self.assertEqual(hash3, hash4)


game_sequence = [
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
]

game_sequence_boring = [
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
]
