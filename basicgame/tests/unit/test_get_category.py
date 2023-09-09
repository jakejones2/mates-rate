from basicgame.utils import get_category
from basicgame.tests.unit.base import TripleTest, hash_database_async


class TestGetCategory(TripleTest):
    """
    Takes game id.
    Function should find one category amongst submission
    fields in the database. Should have no side effects.
    """

    async def test_finds_one_category(self):
        await self.update_submissions("char1", "char2", "_category")
        output = await get_category(self.test_game.pk)
        self.assertEqual(output, "category")

    async def test_if_two_categories_picks_one(self):
        await self.update_submissions("char1", "_category1", "_category2")
        output = await get_category(self.test_game.id)
        self.assertEqual(output, "category1")

    async def test_does_not_modify_db(self):
        hash1 = await hash_database_async()
        await get_category(self.test_game.id)
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)
