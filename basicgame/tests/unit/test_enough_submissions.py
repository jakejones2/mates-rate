from basicgame.utils import enough_submissions
from basicgame.tests.unit.base import TripleTest, hash_database_async


class TestEnoughSubmissions(TripleTest):
    """
    Takes game_id. Iterates through players returning true
    if one category (starting with _) and character is present.
    Otherwise returns false. Has no side effects.
    """

    async def test_returns_true_correctly(self):
        await self.seed_db()
        output = await enough_submissions(self.test_game.pk)
        self.assertTrue(output)

    async def test_returns_false_when_category_missing(self):
        await self.update_submissions("dog", "cat", "mouse")
        output = await enough_submissions(self.test_game.pk)
        self.assertFalse(output)

    async def test_returns_false_when_character_missing(self):
        await self.update_submissions("_dog", None, None)
        output = await enough_submissions(self.test_game.pk)
        self.assertFalse(output)

    async def test_returns_false_when_character_and_category_missing(self):
        await self.update_submissions(None, None, None)
        output = await enough_submissions(self.test_game.pk)
        self.assertFalse(output)

    async def test_returns_false_with_multiple_categories_but_no_character(self):
        await self.update_submissions("_dog", "_fish", None)
        output = await enough_submissions(self.test_game.pk)
        self.assertFalse(output)

    async def test_does_not_mutate_database(self):
        # check with a false response
        await self.update_submissions("_dog", "_fish", None)
        hash1 = await hash_database_async()
        await enough_submissions(self.test_game.pk)
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)
        # check with a true response
        await self.update_submissions("_dog", "fish", None)
        hash1 = await hash_database_async()
        await enough_submissions(self.test_game.pk)
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)
