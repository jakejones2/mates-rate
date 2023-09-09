from basicgame.utils import create_average_score_dict
from basicgame.tests.unit.base import TripleTest, hash_database_async


class TestCreateAverageScoreDict(TripleTest):
    """
    Function should take a game_id, and extract scores
    from all players for each character. Computes an average and
    rounds to it. Returns a dictionary of characters and integer scores.
    Should have no side effects.
    """

    async def test_should_create_correct_averages(self):
        await self.seed_db()
        output = await create_average_score_dict(self.test_game.pk)
        expected = {"cat": 40, "dog": 60}
        self.assertEqual(output, expected)

    async def test_should_skip_players_with_no_votes(self):
        await self.seed_db()
        await self.update_user1_vote(None)
        output = await create_average_score_dict(self.test_game.pk)
        expected = {"cat": 50, "dog": 50}
        self.assertEqual(output, expected)

    async def test_should_round_to_integer(self):
        await self.seed_db()
        await self.update_user1_vote(
            '{"vote":{"name":"testuser112345678","voteData":{"category":"pets","characterScores":{"dog":"83","cat":"27"}}}}'
        )
        output = await create_average_score_dict(self.test_game.pk)
        expected = {"cat": 42, "dog": 61}
        self.assertEqual(output, expected)

    async def test_should_only_process_votes_of_given_game(self):
        await self.seed_db()
        await self.seed_new_game()
        output = await create_average_score_dict(self.test_game.pk)
        expected = {"cat": 40, "dog": 60}
        self.assertEqual(output, expected)

    async def test_should_not_modify_database(self):
        await self.seed_db()
        hash1 = await hash_database_async()
        await create_average_score_dict(self.test_game.pk)
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)
