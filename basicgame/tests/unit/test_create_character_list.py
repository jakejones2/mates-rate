from basicgame.utils import create_character_list
from basicgame.tests.unit.base import TripleTest, hash_database_async


class TestCreateCharacterList(TripleTest):
    """
    Function should return a list of characters, without the
    category and None values. Should have no side effects.
    """

    async def test_should_find_characters(self):
        await self.update_submissions("char1", "char2", "char3")
        output = await create_character_list(self.test_game.pk)
        self.assertEqual(output, ["char1", "char2", "char3"])

    async def test_should_discount_category(self):
        await self.update_submissions("char1", "_category", "char3")
        output = await create_character_list(self.test_game.pk)
        self.assertEqual(output, ["char1", "char3"])

    async def test_should_discount_none_values(self):
        await self.update_submissions(None, "_category", "char3")
        output = await create_character_list(self.test_game.pk)
        self.assertEqual(output, ["char3"])

    async def test_should_not_modify_db(self):
        hash1 = await hash_database_async()
        await create_character_list(self.test_game.pk)
        hash2 = await hash_database_async()
        self.assertEqual(hash1, hash2)
