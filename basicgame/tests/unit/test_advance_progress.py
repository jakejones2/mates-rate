from basicgame.utils import advance_progress
from basicgame.tests.unit.base import TripleTest, hash_database_async


class TestAdvanceProgress(TripleTest):
    """
    Increments game progress to index of given round name in game sequence.
    If this round is already reached, nothing changes.
    Does not mutate game sequence, or alter the database other than the
    progress field.
    """

    # submission to vote

    async def test_advances_from_submission_to_vote(self):
        await self.set_game_progress(0)
        await advance_progress(self.test_game.pk, "vote", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 1)

    async def test_does_not_advance_to_vote_if_already_at_vote(self):
        await self.set_game_progress(1)
        await advance_progress(self.test_game.pk, "vote", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 1)

    async def test_advances_from_submission_to_vote_in_later_rounds(self):
        # round 2
        await self.set_game_progress(5)
        await advance_progress(self.test_game.pk, "vote", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 6)
        # round 3
        await self.set_game_progress(10)
        await advance_progress(self.test_game.pk, "vote", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 11)

    async def test_does_not_advance_to_vote_if_already_at_vote_in_later_rounds(self):
        # round 2
        await self.set_game_progress(6)
        await advance_progress(self.test_game.pk, "vote", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 6)
        # round 3
        await self.set_game_progress(11)
        await advance_progress(self.test_game.pk, "vote", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 11)

    # vote to winner

    async def test_advances_from_vote_to_winner(self):
        # round 1
        await self.set_game_progress(1)
        await advance_progress(self.test_game.pk, "winner", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 2)
        # round 2
        await self.set_game_progress(6)
        await advance_progress(self.test_game.pk, "winner", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 7)
        # round 3
        await self.set_game_progress(11)
        await advance_progress(self.test_game.pk, "winner", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 12)

    async def test_does_not_advance_to_winner_if_already_at_winner(self):
        # round 1
        await self.set_game_progress(2)
        await advance_progress(self.test_game.pk, "winner", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 2)
        # round 3
        await self.set_game_progress(12)
        await advance_progress(self.test_game.pk, "winner", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 12)

    async def test_advances_from_winner_to_results(self):
        # round 1
        await self.set_game_progress(2)
        await advance_progress(self.test_game.pk, "results", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 3)
        # round 2
        await self.set_game_progress(7)
        await advance_progress(self.test_game.pk, "results", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 8)

    async def test_does_not_advance_to_results_if_already_at_results(self):
        # round 1
        await self.set_game_progress(3)
        await advance_progress(self.test_game.pk, "results", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 3)
        # round 3
        await self.set_game_progress(13)
        await advance_progress(self.test_game.pk, "results", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 13)

    async def test_advances_from_results_to_leaderboard(self):
        # round 1
        await self.set_game_progress(3)
        await advance_progress(self.test_game.pk, "leaderboard", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 4)
        # round 3
        await self.set_game_progress(13)
        await advance_progress(self.test_game.pk, "leaderboard", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 14)

    async def test_does_not_advance_to_leaderboard_if_already_at_leaderboard(self):
        # round 2
        await self.set_game_progress(9)
        await advance_progress(self.test_game.pk, "leaderboard", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 9)
        # round 3
        await self.set_game_progress(14)
        await advance_progress(self.test_game.pk, "leaderboard", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 14)

    async def test_advances_from_leaderboard_to_submission(self):
        # round 1
        await self.set_game_progress(4)
        await advance_progress(self.test_game.pk, "submission", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 5)
        # round 2
        await self.set_game_progress(9)
        await advance_progress(self.test_game.pk, "submission", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 10)

    async def test_does_not_advance_to_submission_if_already_at_submission(self):
        # round 2
        await self.set_game_progress(10)
        await advance_progress(self.test_game.pk, "submission", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 10)
        # round 3
        await self.set_game_progress(15)
        await advance_progress(self.test_game.pk, "submission", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 15)

    async def test_does_not_mutate_db_other_than_progress(self):
        # example 1: submission to vote round 1
        await self.set_game_progress(0)
        hash1 = await hash_database_async(discounted=["progress"])
        await advance_progress(self.test_game.pk, "vote", game_sequence.copy())
        hash2 = await hash_database_async(discounted=["progress"])
        self.assertEqual(hash1, hash2)
        # example 2: leaderboard to leaderboard round 2
        await self.set_game_progress(9)
        hash1 = await hash_database_async(discounted=["progress"])
        await advance_progress(self.test_game.pk, "leaderboard", game_sequence.copy())
        hash2 = await hash_database_async(discounted=["progress"])
        self.assertEqual(hash1, hash2)
        # example 3: leaderboard to finish round 3
        await self.set_game_progress(14)
        hash1 = await hash_database_async(discounted=["progress"])
        await advance_progress(self.test_game.pk, "submission", game_sequence.copy())
        hash2 = await hash_database_async(discounted=["progress"])
        self.assertEqual(hash1, hash2)

    async def test_does_not_mutate_game_sequence(self):
        # example 1: winner to results round 1
        await self.set_game_progress(2)
        game_sequence_copy = game_sequence.copy()
        game_sequence_copy2 = game_sequence.copy()
        await advance_progress(self.test_game.pk, "results", game_sequence_copy)
        self.assertEqual(game_sequence_copy2, game_sequence_copy)
        # example 1: vote to winner round 2
        await self.set_game_progress(11)
        await advance_progress(self.test_game.pk, "winner", game_sequence_copy)
        self.assertEqual(game_sequence_copy2, game_sequence_copy)
        # example 1: vote to vote round 3
        await self.set_game_progress(11)
        await advance_progress(self.test_game.pk, "vote", game_sequence_copy)
        self.assertEqual(game_sequence_copy2, game_sequence_copy)

    async def test_advances_to_character_in_boring_mode(self):
        # submission to character
        await self.set_game_progress(0)
        await advance_progress(
            self.test_game.pk, "character", game_sequence_boring.copy()
        )
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 1)
        # fails with wrong sequence
        await self.set_game_progress(0)
        await advance_progress(self.test_game.pk, "character", game_sequence.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 0)
        # works on round 2 (each cycle has 6 views)
        await self.set_game_progress(6)
        await advance_progress(
            self.test_game.pk, "character", game_sequence_boring.copy()
        )
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 7)

    async def test_advances_to_vote_in_boring_mode(self):
        # round 3 (each cycle has 6 views)
        await self.set_game_progress(13)
        await advance_progress(self.test_game.pk, "vote", game_sequence_boring.copy())
        new_prog = await self.get_game_progress()
        self.assertEqual(new_prog, 14)


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
