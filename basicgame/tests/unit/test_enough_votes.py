from basicgame.utils import enough_votes
from basicgame.tests.unit.base import TripleTest, hash_database_async


class TestEnoughVotes(TripleTest):
    """
    Takes game_id. Iterates through players in game to see if
    any votes have been submitted. Returns false if none found.
    """

    async def test_returns_true_with_all_votes(self):
        await self.seed_db()
        output = await enough_votes(self.test_game.pk)
        self.assertTrue(output)

    async def test_returns_true_with_only_one_vote(self):
        await self.update_votes(None, None, "something")
        output = await enough_votes(self.test_game.pk)
        self.assertTrue(output)

    async def test_returns_false_with_no_votes(self):
        await self.update_votes(None, None, None)
        output = await enough_votes(self.test_game.pk)
        self.assertFalse(output)

    async def test_does_not_modify_database(self):
        await self.update_votes(None, None, None)
        hash1 = await hash_database_async()
        await enough_votes(self.test_game.pk)
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)
        # check with a true response
        await self.update_votes(None, 12, 14)
        hash1 = await hash_database_async()
        await enough_votes(self.test_game.pk)
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)
